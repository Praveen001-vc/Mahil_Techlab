from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ContactMessage, Enrollment


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
        fields = ["phone", "course", "experience", "notes"]
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+1 ..."}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = self.fields["course"].queryset.filter(is_active=True)


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
