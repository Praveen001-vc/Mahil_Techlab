from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from allauth.socialaccount.models import SocialApp

from .forms import (
    AdminUserCreateForm,
    AdminUserEditForm,
    ContactForm,
    EnrollmentForm,
    SignUpForm,
)
from .models import Course, Project


def _safe_next_url(request, fallback_name="home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse(fallback_name)


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


def home(request):
    featured_courses = Course.objects.filter(is_active=True).order_by("title")[:3]
    featured_projects = Project.objects.filter(is_active=True).order_by("display_order", "name")[:3]
    for project in featured_projects:
        project.install_link = _project_install_url(request, project)
    context = {
        "featured_courses": featured_courses,
        "featured_projects": featured_projects,
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
    preselect_slug = request.GET.get("course")
    if preselect_slug:
        preselected_course = course_qs.filter(slug=preselect_slug).first()
        if preselected_course:
            initial["course"] = preselected_course

    if request.method == "POST" and not request.user.is_authenticated:
        messages.info(request, "Please register and log in to apply for a course.")
        return redirect(f"{reverse('register')}?next={quote(request.get_full_path())}")

    if request.method == "POST" and request.user.is_authenticated and not request.user.email:
        messages.error(
            request,
            "Your account is missing an email address. Please update your profile before applying.",
        )
        return redirect("courses")

    can_apply = request.user.is_authenticated and bool(request.user.email)

    if can_apply:
        if request.method == "POST":
            form = EnrollmentForm(request.POST)
            if form.is_valid():
                enrollment = form.save(commit=False)
                enrollment.user = request.user
                enrollment.name = request.user.get_full_name().strip() or request.user.username
                enrollment.email = request.user.email
                enrollment.save()
                messages.success(request, "Enrollment request submitted successfully.")
                return redirect(f"{reverse('courses')}#enroll-form")
            messages.error(request, "Please correct the form errors and submit again.")
        else:
            form = EnrollmentForm(initial=initial)
    else:
        form = None

    context = {"courses": course_qs, "enrollment_form": form}
    return render(request, "core/courses.html", context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
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

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login successful.")
            return redirect(_safe_next_url(request, fallback_name="home"))
        messages.error(request, "Invalid username or password.")
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


def admin_users(request):
    guard_response = _require_superuser(request)
    if guard_response:
        return guard_response

    search_query = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("-date_joined")
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    if request.method == "POST":
        create_form = AdminUserCreateForm(request.POST)
        if create_form.is_valid():
            created_user = create_form.save()
            messages.success(request, f"User '{created_user.username}' was created successfully.")
            return redirect("admin_users")
        messages.error(request, "Please correct the user creation form errors.")
    else:
        create_form = AdminUserCreateForm()

    return render(
        request,
        "core/admin_users.html",
        {
            "create_form": create_form,
            "users": users,
            "search_query": search_query,
        },
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
                return redirect("admin_users")
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
        return redirect("admin_users")

    target_user = get_object_or_404(User, pk=user_id)

    if target_user == request.user:
        messages.error(request, "You cannot delete your own account while logged in.")
        return redirect("admin_users")

    if target_user.is_superuser:
        superuser_count = User.objects.filter(is_superuser=True).count()
        if superuser_count <= 1:
            messages.error(request, "Cannot delete the last superuser account.")
            return redirect("admin_users")

    deleted_username = target_user.username
    target_user.delete()
    messages.success(request, f"User '{deleted_username}' was deleted successfully.")
    return redirect("admin_users")
