from django.urls import path

from . import views

urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("downloads/mahilmart-pos/setup/", views.download_pos_installer, name="download_pos_installer"),
    path("", views.home, name="home"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("courses/", views.courses, name="courses"),
    path("courses/enrollment-submitted/", views.enrollment_submitted, name="enrollment_submitted"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("admin-access/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-access/messages/", views.admin_contact_messages, name="admin_contact_messages"),
    path("admin-access/enrollments/", views.admin_enrollments, name="admin_enrollments"),
    path("admin-access/users/", views.admin_users, name="admin_users"),
    path("admin-access/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("admin-access/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("admin-access/courses/", views.admin_courses, name="admin_courses"),
    path("admin-access/sliders/", views.admin_sliders, name="admin_sliders"),
    path("admin-access/sliders/<int:slider_id>/edit/", views.admin_slider_edit, name="admin_slider_edit"),
    path(
        "admin-access/sliders/<int:slider_id>/delete/",
        views.admin_slider_delete,
        name="admin_slider_delete",
    ),
    path(
        "admin-access/sliders/<int:slider_id>/toggle-live/",
        views.admin_slider_toggle_live,
        name="admin_slider_toggle_live",
    ),
    path("admin-access/courses/<int:course_id>/edit/", views.admin_course_edit, name="admin_course_edit"),
    path(
        "admin-access/courses/<int:course_id>/delete/",
        views.admin_course_delete,
        name="admin_course_delete",
    ),
    path(
        "admin-access/courses/<int:course_id>/toggle-live/",
        views.admin_course_toggle_live,
        name="admin_course_toggle_live",
    ),
]
