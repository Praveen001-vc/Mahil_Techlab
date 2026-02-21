from django.conf import settings
from django.db import models


class Course(models.Model):
    LEVEL_CHOICES = (
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    )

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    duration_weeks = models.PositiveSmallIntegerField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    fee_usd = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=180)
    company = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Enrollment(models.Model):
    EXPERIENCE_CHOICES = (
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    )

    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=180)
    phone = models.CharField(max_length=40, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments")
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default="Beginner")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.course.title}"


class Project(models.Model):
    name = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    icon_url = models.URLField(blank=True)
    tagline = models.CharField(max_length=220, blank=True)
    short_description = models.TextField()
    details = models.TextField(blank=True)
    install_url = models.URLField(blank=True)
    version = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name
