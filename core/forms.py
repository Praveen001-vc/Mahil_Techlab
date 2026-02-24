from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import ContactMessage, Course, Enrollment, HomeSlider


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "company", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "company": forms.TextInput(attrs={"placeholder": "Company name (optional)"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell us what you need"}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["email", "phone", "course", "experience", "notes"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+1 ..."}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = self.fields["course"].queryset.filter(is_active=True)
        self.fields["email"].help_text = "Use an active inbox. Confirmation email will be sent here."


class AdminCourseForm(forms.ModelForm):
    slug = forms.SlugField(max_length=220, required=False)

    class Meta:
        model = Course
        fields = [
            "title",
            "slug",
            "description",
            "duration_weeks",
            "level",
            "fee_usd",
            "fee_currency",
            "is_active",
        ]
        labels = {
            "fee_usd": "Fee Amount",
            "fee_currency": "Fee Currency",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Course title"}),
            "slug": forms.TextInput(attrs={"placeholder": "auto-from-title (optional)"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Course details and outcomes"}
            ),
            "duration_weeks": forms.NumberInput(attrs={"min": 1}),
            "fee_usd": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        title = self.cleaned_data.get("title", "").strip()
        if slug:
            return slug
        return slugify(title)

    def clean(self):
        cleaned = super().clean()
        slug = cleaned.get("slug", "").strip()
        title = cleaned.get("title", "").strip()

        if title and not slug:
            self.add_error("slug", "Slug cannot be empty. Add a slug or provide a valid title.")
            return cleaned

        if slug:
            qs = Course.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("slug", "A course with this slug already exists.")

        return cleaned


class AdminSliderForm(forms.ModelForm):
    class Meta:
        model = HomeSlider
        fields = [
            "title",
            "subtitle",
            "image",
            "button_label",
            "button_url",
            "display_order",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Slide title"}),
            "subtitle": forms.TextInput(attrs={"placeholder": "Optional subtitle"}),
            "button_label": forms.TextInput(attrs={"placeholder": "Optional button text"}),
            "button_url": forms.TextInput(attrs={"placeholder": "/contact or https://..."}),
            "display_order": forms.NumberInput(attrs={"min": 0}),
        }


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(max_length=180, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name (optional)"}),
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class AdminUserCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(max_length=180, required=True)
    is_active = forms.BooleanField(required=False, initial=True)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "").strip()
        user.last_name = self.cleaned_data.get("last_name", "").strip()
        user.email = self.cleaned_data.get("email", "").strip().lower()
        user.is_active = bool(self.cleaned_data.get("is_active"))
        user.is_staff = bool(self.cleaned_data.get("is_staff"))
        user.is_superuser = bool(self.cleaned_data.get("is_superuser"))

        if user.is_superuser:
            user.is_staff = True

        if commit:
            user.save()
        return user


class AdminUserEditForm(forms.ModelForm):
    email = forms.EmailField(max_length=180, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        is_superuser = bool(cleaned.get("is_superuser"))

        if not is_superuser and self.instance.is_superuser:
            remaining_superusers = User.objects.filter(is_superuser=True).exclude(pk=self.instance.pk).count()
            if remaining_superusers == 0:
                self.add_error("is_superuser", "At least one superuser must remain in the system.")

        if is_superuser:
            cleaned["is_staff"] = True

        return cleaned
