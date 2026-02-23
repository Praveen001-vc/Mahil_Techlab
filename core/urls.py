from django.urls import path

from . import views

urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("downloads/mahilmart-pos/setup/", views.download_pos_installer, name="download_pos_installer"),
    path("", views.home, name="home"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("courses/", views.courses, name="courses"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("admin-access/users/", views.admin_users, name="admin_users"),
    path("admin-access/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("admin-access/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),
]
