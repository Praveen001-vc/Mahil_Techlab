from django.contrib import admin

from .models import ContactMessage, Course, Enrollment, HomeSlider, Project


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "duration_weeks", "fee_usd", "fee_currency", "is_active")
    list_filter = ("level", "fee_currency", "is_active")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "created_at")
    search_fields = ("name", "email", "company", "message")
    readonly_fields = ("created_at",)


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "button_label", "button_url")
    readonly_fields = ("created_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "user", "course", "experience", "created_at")
    list_filter = ("experience", "course")
    search_fields = ("name", "email", "phone", "notes")
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active", "display_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "tagline", "short_description", "details")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
