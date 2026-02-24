from pathlib import Path
import logging
import math
from urllib.parse import quote, urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.utils.timezone import localtime

from allauth.socialaccount.models import SocialApp

from .forms import (
    AdminCourseForm,
    AdminSliderForm,
    AdminUserCreateForm,
    AdminUserEditForm,
    ContactForm,
    EnrollmentForm,
    SignUpForm,
)
from .models import ContactMessage, Course, Enrollment, HomeSlider, Project

logger = logging.getLogger(__name__)


def _safe_next_url(request, fallback_name="home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse(fallback_name)


def _admin_dashboard_url(panel="", **params):
    query = {}
    if panel:
        query["panel"] = panel
    for key, value in params.items():
        if value is None:
            continue
        string_value = str(value).strip()
        if string_value:
            query[key] = string_value
    base_url = reverse("admin_dashboard")
    if not query:
        return base_url
    return f"{base_url}?{urlencode(query)}"


def _require_superuser(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")
    if not request.user.is_superuser:
        messages.error(request, "Only admin users can access this page.")
        return redirect("home")
    return None


def _google_login_enabled():
    if (
        getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
        and getattr(settings, "GOOGLE_CLIENT_SECRET", "").strip()
    ):
        return True
    return SocialApp.objects.filter(provider="google").exists()


def _resolve_pos_installer_path():
    configured_path = getattr(settings, "POS_INSTALLER_PATH", "").strip()
    if not configured_path:
        return None

    installer_path = Path(configured_path).expanduser()
    if not installer_path.is_absolute():
        installer_path = Path(settings.BASE_DIR) / installer_path
    return installer_path


def _pos_installer_enabled():
    if getattr(settings, "POS_INSTALLER_URL", "").strip():
        return True
    installer_path = _resolve_pos_installer_path()
    return bool(installer_path and installer_path.is_file())


def _project_install_url(request, project):
    if not request.user.is_authenticated:
        return ""
    if project.install_url:
        return project.install_url
    if _pos_installer_enabled():
        return reverse("download_pos_installer")
    return ""


def _validated_email(raw_value):
    email = str(raw_value or "").strip()
    if not email:
        return ""
    try:
        validate_email(email)
        return email
    except ValidationError:
        logger.warning("Invalid email address configured or submitted: %s", email)
        return ""


def _send_contact_notification_email(request, contact_message):
    recipient_email = getattr(settings, "CONTACT_RECEIVER_EMAIL", "").strip()
    if not recipient_email:
        return

    submitted_at = localtime(contact_message.created_at).strftime("%Y-%m-%d %H:%M:%S %Z")
    messages_url = request.build_absolute_uri(_admin_dashboard_url(panel="messages"))
    message_url = request.build_absolute_uri(
        _admin_dashboard_url(panel="messages", message=contact_message.id)
    )
    email_subject = f"New Contact Message: {contact_message.name}"
    email_context = {
        "contact_message": contact_message,
        "submitted_at": submitted_at,
        "messages_url": messages_url,
        "message_url": message_url,
        "site_host": request.get_host(),
    }
    email_text = render_to_string("core/emails/contact_notification.txt", email_context)
    email_html = render_to_string("core/emails/contact_notification.html", email_context)

    email = EmailMultiAlternatives(
        subject=email_subject,
        body=email_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
        reply_to=[contact_message.email],
    )
    email.attach_alternative(email_html, "text/html")
    email.send(fail_silently=False)


def _send_contact_acknowledgement_email(request, contact_message):
    email_context = {
        "contact_message": contact_message,
        "site_host": request.get_host(),
    }
    email_subject = "Thank you for contacting Mahil Techlab"
    email_text = render_to_string("core/emails/contact_acknowledgement.txt", email_context)
    email_html = render_to_string("core/emails/contact_acknowledgement.html", email_context)

    email = EmailMultiAlternatives(
        subject=email_subject,
        body=email_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contact_message.email],
    )
    email.attach_alternative(email_html, "text/html")
    email.send(fail_silently=False)


def _send_enrollment_notification_email(request, enrollment):
    candidate_recipients = [
        getattr(settings, "ENROLLMENT_RECEIVER_EMAIL", ""),
        getattr(settings, "CONTACT_RECEIVER_EMAIL", ""),
    ]
    recipients = []
    for candidate in candidate_recipients:
        valid_email = _validated_email(candidate)
        if valid_email and valid_email not in recipients:
            recipients.append(valid_email)
    if not recipients:
        return False

    submitted_at = localtime(enrollment.created_at).strftime("%Y-%m-%d %H:%M:%S %Z")
    enrollments_url = request.build_absolute_uri(_admin_dashboard_url(panel="enrollments"))
    enrollment_url = request.build_absolute_uri(
        _admin_dashboard_url(panel="enrollments", enrollment=enrollment.id)
    )
    try:
        enrollments_admin_url = request.build_absolute_uri(reverse("admin:core_enrollment_changelist"))
    except NoReverseMatch:
        enrollments_admin_url = enrollments_url

    email_context = {
        "enrollment": enrollment,
        "submitted_at": submitted_at,
        "enrollments_url": enrollments_url,
        "enrollment_url": enrollment_url,
        "enrollments_admin_url": enrollments_admin_url,
        "site_host": request.get_host(),
    }
    email_subject = f"New Enrollment Application: {enrollment.name} - {enrollment.course.title}"
    email_text = render_to_string("core/emails/enrollment_notification.txt", email_context)
    email_html = render_to_string("core/emails/enrollment_notification.html", email_context)

    email = EmailMultiAlternatives(
        subject=email_subject,
        body=email_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[enrollment.email],
    )
    email.attach_alternative(email_html, "text/html")
    email.send(fail_silently=False)
    return True


def _send_enrollment_acknowledgement_email(request, enrollment):
    recipient_email = _validated_email(enrollment.email)
    if not recipient_email:
        return False

    email_context = {
        "enrollment": enrollment,
        "site_host": request.get_host(),
    }
    email_subject = f"Enrollment Received: {enrollment.course.title}"
    email_text = render_to_string("core/emails/enrollment_acknowledgement.txt", email_context)
    email_html = render_to_string("core/emails/enrollment_acknowledgement.html", email_context)

    email = EmailMultiAlternatives(
        subject=email_subject,
        body=email_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.attach_alternative(email_html, "text/html")
    email.send(fail_silently=False)
    return True


def home(request):
    featured_courses = Course.objects.filter(is_active=True).order_by("title")[:3]
    featured_projects = Project.objects.filter(is_active=True).order_by("display_order", "name")[:3]
    home_slides = HomeSlider.objects.filter(is_active=True).order_by("display_order", "-created_at")
    for project in featured_projects:
        project.install_link = _project_install_url(request, project)
    context = {
        "featured_courses": featured_courses,
        "featured_projects": featured_projects,
        "home_slides": home_slides,
        "pos_installer_enabled": request.user.is_authenticated and _pos_installer_enabled(),
    }
    return render(request, "core/home.html", context)


def healthz(_request):
    return JsonResponse({"ok": True, "service": "mahil-techlab"})


def projects(request):
    project_qs = Project.objects.filter(is_active=True).order_by("display_order", "name")
    project_cards = list(project_qs)
    for project in project_cards:
        project.install_link = _project_install_url(request, project)
    return render(request, "core/projects.html", {"projects": project_cards})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_active=True)
    return render(
        request,
        "core/project_detail.html",
        {
            "project": project,
            "install_link": _project_install_url(request, project),
        },
    )


def courses(request):
    course_qs = Course.objects.filter(is_active=True).order_by("title")
    initial = {}
    if request.user.is_authenticated and request.user.email:
        initial["email"] = request.user.email
    preselect_slug = request.GET.get("course")
    if preselect_slug:
        preselected_course = course_qs.filter(slug=preselect_slug).first()
        if preselected_course:
            initial["course"] = preselected_course

    if request.method == "POST" and not request.user.is_authenticated:
        messages.info(request, "Please register and log in to apply for a course.")
        return redirect(f"{reverse('register')}?next={quote(request.get_full_path())}")

    can_apply = request.user.is_authenticated

    if can_apply:
        if request.method == "POST":
            form = EnrollmentForm(request.POST)
            if form.is_valid():
                enrollment = form.save(commit=False)
                enrollment.user = request.user
                enrollment.name = request.user.get_full_name().strip() or request.user.username
                enrollment.email = form.cleaned_data["email"].strip().lower()
                enrollment.save()

                admin_alert_failed = False
                admin_alert_skipped = False
                acknowledgement_failed = False
                acknowledgement_skipped = False
                try:
                    admin_alert_sent = _send_enrollment_notification_email(request, enrollment)
                    if not admin_alert_sent:
                        admin_alert_skipped = True
                except Exception:
                    admin_alert_failed = True
                    logger.exception("Enrollment saved, but email delivery failed.")
                try:
                    acknowledgement_sent = _send_enrollment_acknowledgement_email(request, enrollment)
                    if not acknowledgement_sent:
                        acknowledgement_skipped = True
                except Exception:
                    acknowledgement_failed = True
                    logger.exception("Enrollment saved, but acknowledgement email delivery failed.")

                if admin_alert_skipped:
                    messages.warning(
                        request,
                        "Enrollment submitted, but enrollment alert recipient email is not configured correctly.",
                    )
                if admin_alert_failed:
                    messages.warning(
                        request,
                        "Enrollment submitted, but internal alert email delivery failed.",
                    )
                if acknowledgement_skipped:
                    messages.warning(
                        request,
                        "Enrollment submitted, but confirmation email address is invalid.",
                    )
                if acknowledgement_failed:
                    messages.warning(
                        request,
                        "Enrollment submitted, but confirmation email could not be delivered to you.",
                    )

                messages.success(request, "Enrollment request submitted successfully.")
                return redirect(f"{reverse('enrollment_submitted')}?id={enrollment.id}")
            messages.error(request, "Please correct the form errors and submit again.")
        else:
            form = EnrollmentForm(initial=initial)
    else:
        form = None

    context = {"courses": course_qs, "enrollment_form": form}
    return render(request, "core/courses.html", context)


def enrollment_submitted(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")

    enrollment_id_raw = request.GET.get("id", "").strip()
    if not enrollment_id_raw.isdigit():
        messages.info(request, "Submit an enrollment request to view this page.")
        return redirect("courses")

    enrollment = (
        Enrollment.objects.filter(pk=int(enrollment_id_raw), user=request.user)
        .select_related("course")
        .first()
    )
    if not enrollment:
        messages.error(request, "Enrollment record was not found.")
        return redirect("courses")

    return render(request, "core/enrollment_submitted.html", {"enrollment": enrollment})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            admin_alert_failed = False
            acknowledgement_failed = False
            try:
                _send_contact_notification_email(request, contact_message)
            except Exception:
                admin_alert_failed = True
                logger.exception("Contact message saved, but admin alert email delivery failed.")
            try:
                _send_contact_acknowledgement_email(request, contact_message)
            except Exception:
                acknowledgement_failed = True
                logger.exception("Contact message saved, but acknowledgement email delivery failed.")

            if admin_alert_failed:
                messages.warning(
                    request,
                    "Your message was saved, but internal alert email delivery failed.",
                )
            if acknowledgement_failed:
                messages.warning(
                    request,
                    "Your message was received, but confirmation email could not be delivered to you.",
                )
            messages.success(request, "Thank you. Your message has been received.")
            return redirect("contact")
        messages.error(request, "Please correct the form errors and submit again.")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"contact_form": form})


def register_user(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request, fallback_name="home"))

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect(_safe_next_url(request, fallback_name="home"))
        messages.error(request, "Please correct the form errors and try again.")
    else:
        form = SignUpForm()

    return render(
        request,
        "core/register.html",
        {
            "register_form": form,
            "next_url": _safe_next_url(request, fallback_name="home"),
            "google_login_enabled": _google_login_enabled(),
        },
    )


def login_user(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request, fallback_name="home"))

    max_attempts = max(1, int(getattr(settings, "MAX_LOGIN_ATTEMPTS", 5)))
    lockout_seconds = max(60, int(getattr(settings, "LOGIN_LOCKOUT_SECONDS", 900)))
    now_timestamp = int(timezone.now().timestamp())
    lock_until = int(request.session.get("login_lock_until_ts", 0) or 0)

    if lock_until and now_timestamp >= lock_until:
        request.session.pop("login_lock_until_ts", None)
        request.session.pop("login_failed_attempts", None)
        lock_until = 0

    if request.method == "POST" and lock_until and now_timestamp < lock_until:
        remaining_seconds = lock_until - now_timestamp
        wait_minutes = max(1, math.ceil(remaining_seconds / 60))
        messages.error(
            request,
            f"Too many failed login attempts. Try again in {wait_minutes} minute(s).",
        )
        form = AuthenticationForm(request)
    elif request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            request.session.pop("login_lock_until_ts", None)
            request.session.pop("login_failed_attempts", None)
            messages.success(request, "Login successful.")
            return redirect(_safe_next_url(request, fallback_name="home"))

        failed_attempts = int(request.session.get("login_failed_attempts", 0) or 0) + 1
        if failed_attempts >= max_attempts:
            lock_until_ts = now_timestamp + lockout_seconds
            wait_minutes = max(1, math.ceil(lockout_seconds / 60))
            request.session["login_failed_attempts"] = 0
            request.session["login_lock_until_ts"] = lock_until_ts
            messages.error(
                request,
                f"Too many failed login attempts. Try again in {wait_minutes} minute(s).",
            )
            form = AuthenticationForm(request)
        else:
            request.session["login_failed_attempts"] = failed_attempts
            attempts_left = max_attempts - failed_attempts
            messages.error(
                request,
                f"Invalid username or password. {attempts_left} attempt(s) left.",
            )
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "core/login.html",
        {
            "login_form": form,
            "next_url": _safe_next_url(request, fallback_name="home"),
            "google_login_enabled": _google_login_enabled(),
        },
    )


def logout_user(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("home")


def download_pos_installer(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to download the installer.")
        return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")

    installer_url = getattr(settings, "POS_INSTALLER_URL", "").strip()
    if installer_url:
        return redirect(installer_url)

    installer_path = _resolve_pos_installer_path()
    if not installer_path or not installer_path.is_file():
        messages.error(request, "Installer file not found. Build the Inno Setup package and try again.")
        return redirect("home")

    filename = getattr(settings, "POS_INSTALLER_FILENAME", "").strip() or installer_path.name
    return FileResponse(
        installer_path.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/octet-stream",
    )


def admin_dashboard(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    messages_query = request.GET.get("messages_q", "").strip()
    enrollments_query = request.GET.get("enrollments_q", "").strip()
    courses_query = request.GET.get("courses_q", "").strip()
    users_query = request.GET.get("users_q", "").strip()
    sliders_query = request.GET.get("sliders_q", "").strip()
    focus_message_id = request.GET.get("message", "").strip()
    focus_enrollment_id = request.GET.get("enrollment", "").strip()
    selected_message_id = int(focus_message_id) if focus_message_id.isdigit() else None
    selected_enrollment_id = int(focus_enrollment_id) if focus_enrollment_id.isdigit() else None
    active_panel = request.GET.get("panel", "").strip().lower()
    if active_panel not in {"messages", "enrollments", "courses", "users", "sliders"}:
        active_panel = "messages"

    if request.method == "POST":
        form_type = request.POST.get("form_type", "").strip()
        if form_type == "create_course":
            create_course_form = AdminCourseForm(request.POST)
            create_user_form = AdminUserCreateForm()
            create_slider_form = AdminSliderForm()
            if create_course_form.is_valid():
                created_course = create_course_form.save()
                messages.success(request, f"Course '{created_course.title}' was created successfully.")
                return redirect(_admin_dashboard_url(panel="courses"))
            active_panel = "courses"
            messages.error(request, "Please correct the course creation form errors.")
        elif form_type == "create_user":
            create_user_form = AdminUserCreateForm(request.POST)
            create_course_form = AdminCourseForm(initial={"is_active": True})
            create_slider_form = AdminSliderForm()
            if create_user_form.is_valid():
                created_user = create_user_form.save()
                messages.success(request, f"User '{created_user.username}' was created successfully.")
                return redirect(_admin_dashboard_url(panel="users"))
            active_panel = "users"
            messages.error(request, "Please correct the user creation form errors.")
        elif form_type == "create_slider":
            create_slider_form = AdminSliderForm(request.POST, request.FILES)
            create_course_form = AdminCourseForm(initial={"is_active": True})
            create_user_form = AdminUserCreateForm()
            if create_slider_form.is_valid():
                created_slide = create_slider_form.save()
                messages.success(request, f"Slider '{created_slide.title}' was created successfully.")
                return redirect(_admin_dashboard_url(panel="sliders"))
            active_panel = "sliders"
            messages.error(request, "Please correct the slider form errors.")
        else:
            create_course_form = AdminCourseForm(initial={"is_active": True})
            create_user_form = AdminUserCreateForm()
            create_slider_form = AdminSliderForm()
            messages.error(request, "Invalid dashboard form submission.")
    else:
        create_course_form = AdminCourseForm(initial={"is_active": True})
        create_user_form = AdminUserCreateForm()
        create_slider_form = AdminSliderForm()

    contact_messages = ContactMessage.objects.all().order_by("-created_at")
    if messages_query:
        contact_messages = contact_messages.filter(
            Q(name__icontains=messages_query)
            | Q(email__icontains=messages_query)
            | Q(company__icontains=messages_query)
            | Q(message__icontains=messages_query)
        )
    elif selected_message_id:
        contact_messages = contact_messages.order_by(
            Case(
                When(pk=selected_message_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            "-created_at",
        )

    enrollments = Enrollment.objects.select_related("course", "user").all().order_by("-created_at")
    if enrollments_query:
        enrollments = enrollments.filter(
            Q(name__icontains=enrollments_query)
            | Q(email__icontains=enrollments_query)
            | Q(phone__icontains=enrollments_query)
            | Q(experience__icontains=enrollments_query)
            | Q(notes__icontains=enrollments_query)
            | Q(course__title__icontains=enrollments_query)
        )
    elif selected_enrollment_id:
        enrollments = enrollments.order_by(
            Case(
                When(pk=selected_enrollment_id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            "-created_at",
        )

    courses = Course.objects.all().order_by("-created_at", "title")
    if courses_query:
        courses = courses.filter(
            Q(title__icontains=courses_query)
            | Q(slug__icontains=courses_query)
            | Q(description__icontains=courses_query)
            | Q(level__icontains=courses_query)
            | Q(fee_currency__icontains=courses_query)
        )

    users = User.objects.all().order_by("-date_joined")
    if users_query:
        users = users.filter(
            Q(username__icontains=users_query)
            | Q(email__icontains=users_query)
            | Q(first_name__icontains=users_query)
            | Q(last_name__icontains=users_query)
        )

    sliders = HomeSlider.objects.all().order_by("display_order", "-created_at")
    if sliders_query:
        sliders = sliders.filter(
            Q(title__icontains=sliders_query)
            | Q(subtitle__icontains=sliders_query)
            | Q(button_label__icontains=sliders_query)
            | Q(button_url__icontains=sliders_query)
        )

    return render(
        request,
        "core/admin_dashboard.html",
        {
            "active_panel": active_panel,
            "messages_query": messages_query,
            "enrollments_query": enrollments_query,
            "courses_query": courses_query,
            "users_query": users_query,
            "sliders_query": sliders_query,
            "selected_message_id": selected_message_id,
            "selected_enrollment_id": selected_enrollment_id,
            "contact_messages": contact_messages,
            "enrollments": enrollments,
            "create_course_form": create_course_form,
            "courses": courses,
            "create_user_form": create_user_form,
            "users": users,
            "create_slider_form": create_slider_form,
            "sliders": sliders,
        },
    )


def admin_contact_messages(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    return redirect(
        _admin_dashboard_url(
            panel="messages",
            messages_q=request.GET.get("q", "").strip(),
            message=request.GET.get("message", "").strip(),
        )
    )


def admin_enrollments(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method == "POST":
        messages.info(request, "Use Admin Dashboard to review enrollments.")
        return redirect(_admin_dashboard_url(panel="enrollments"))

    return redirect(
        _admin_dashboard_url(
            panel="enrollments",
            enrollments_q=request.GET.get("q", "").strip(),
            enrollment=request.GET.get("enrollment", "").strip(),
        )
    )


def admin_users(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method == "POST":
        messages.info(request, "Use Admin Dashboard for user creation.")
        return redirect(_admin_dashboard_url(panel="users"))

    return redirect(
        _admin_dashboard_url(panel="users", users_q=request.GET.get("q", "").strip())
    )


def admin_user_edit(request, user_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    target_user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = AdminUserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            updated_user = form.save(commit=False)

            if target_user == request.user and not form.cleaned_data.get("is_superuser", False):
                messages.error(request, "You cannot remove superuser access from your own account.")
            else:
                updated_user.save()
                messages.success(request, f"User '{updated_user.username}' was updated successfully.")
                return redirect(_admin_dashboard_url(panel="users"))
        else:
            messages.error(request, "Please correct the edit form errors.")
    else:
        form = AdminUserEditForm(instance=target_user)

    return render(
        request,
        "core/admin_user_edit.html",
        {
            "target_user": target_user,
            "edit_form": form,
        },
    )


def admin_user_delete(request, user_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method != "POST":
        return redirect(_admin_dashboard_url(panel="users"))

    target_user = get_object_or_404(User, pk=user_id)

    if target_user == request.user:
        messages.error(request, "You cannot delete your own account while logged in.")
        return redirect(_admin_dashboard_url(panel="users"))

    if target_user.is_superuser:
        superuser_count = User.objects.filter(is_superuser=True).count()
        if superuser_count <= 1:
            messages.error(request, "Cannot delete the last superuser account.")
            return redirect(_admin_dashboard_url(panel="users"))

    deleted_username = target_user.username
    target_user.delete()
    messages.success(request, f"User '{deleted_username}' was deleted successfully.")
    return redirect(_admin_dashboard_url(panel="users"))


def admin_courses(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method == "POST":
        messages.info(request, "Use Admin Dashboard for course creation.")
        return redirect(_admin_dashboard_url(panel="courses"))

    return redirect(
        _admin_dashboard_url(panel="courses", courses_q=request.GET.get("q", "").strip())
    )


def admin_sliders(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method == "POST":
        messages.info(request, "Use Admin Dashboard for slider creation.")
        return redirect(_admin_dashboard_url(panel="sliders"))

    return redirect(
        _admin_dashboard_url(panel="sliders", sliders_q=request.GET.get("q", "").strip())
    )


def admin_slider_edit(request, slider_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    target_slider = get_object_or_404(HomeSlider, pk=slider_id)

    if request.method == "POST":
        form = AdminSliderForm(request.POST, request.FILES, instance=target_slider)
        if form.is_valid():
            updated_slider = form.save()
            messages.success(request, f"Slider '{updated_slider.title}' was updated successfully.")
            return redirect(_admin_dashboard_url(panel="sliders"))
        messages.error(request, "Please correct the slider edit form errors.")
    else:
        form = AdminSliderForm(instance=target_slider)

    return render(
        request,
        "core/admin_slider_edit.html",
        {
            "target_slider": target_slider,
            "edit_form": form,
        },
    )


def admin_slider_delete(request, slider_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method != "POST":
        return redirect(_admin_dashboard_url(panel="sliders"))

    target_slider = get_object_or_404(HomeSlider, pk=slider_id)
    deleted_title = target_slider.title
    target_slider.delete()
    messages.success(request, f"Slider '{deleted_title}' was deleted successfully.")
    return redirect(_admin_dashboard_url(panel="sliders"))


def admin_slider_toggle_live(request, slider_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method != "POST":
        return redirect(_admin_dashboard_url(panel="sliders"))

    target_slider = get_object_or_404(HomeSlider, pk=slider_id)
    target_slider.is_active = not target_slider.is_active
    target_slider.save(update_fields=["is_active"])
    status_label = "Live" if target_slider.is_active else "Off"
    messages.success(request, f"Slider '{target_slider.title}' is now {status_label}.")
    return redirect(_admin_dashboard_url(panel="sliders"))


def admin_course_edit(request, course_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    target_course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":
        form = AdminCourseForm(request.POST, instance=target_course)
        if form.is_valid():
            updated_course = form.save()
            messages.success(request, f"Course '{updated_course.title}' was updated successfully.")
            return redirect(_admin_dashboard_url(panel="courses"))
        messages.error(request, "Please correct the course edit form errors.")
    else:
        form = AdminCourseForm(instance=target_course)

    return render(
        request,
        "core/admin_course_edit.html",
        {
            "target_course": target_course,
            "edit_form": form,
        },
    )


def admin_course_delete(request, course_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method != "POST":
        return redirect(_admin_dashboard_url(panel="courses"))

    target_course = get_object_or_404(Course, pk=course_id)
    deleted_title = target_course.title
    target_course.delete()
    messages.success(request, f"Course '{deleted_title}' was deleted successfully.")
    return redirect(_admin_dashboard_url(panel="courses"))


def admin_course_toggle_live(request, course_id):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    if request.method != "POST":
        return redirect(_admin_dashboard_url(panel="courses"))

    target_course = get_object_or_404(Course, pk=course_id)
    target_course.is_active = not target_course.is_active
    target_course.save(update_fields=["is_active"])
    status_label = "Live" if target_course.is_active else "Off"
    messages.success(request, f"Course '{target_course.title}' is now {status_label}.")
    return redirect(_admin_dashboard_url(panel="courses"))
