"""Authors: w2143865"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

User = get_user_model()

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from apps.teams.models import Team  # adjust this import if needed


User = get_user_model()


class AdminUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",
        }),
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
        }),
    )

    team_ids = forms.ModelMultipleChoiceField(
        label="Teams",
        queryset=Team.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter username",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter first name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter last name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email address",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "is_staff": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "is_superuser": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, teams=None, supports_additional_teams=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.supports_additional_teams = supports_additional_teams
        self.fields["team_ids"].queryset = teams or Team.objects.order_by("team_name", "team_id")

        if not self.is_bound:
            self.fields["is_active"].initial = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two passwords do not match.")

        if password2:
            validate_password(password2, self.instance)

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)

        selected_teams = list(self.cleaned_data.get("team_ids") or [])

        user.set_password(self.cleaned_data["password1"])
        user.team = selected_teams[0] if selected_teams else None

        if commit:
            user.save()

            if self.supports_additional_teams:
                user.additional_teams.set(selected_teams)

        return user
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "username": "Choose a username",
            "email": "example@sky.com",
            "password1": "Create a password",
            "password2": "Confirm your password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "auth-input",
                    "placeholder": placeholders.get(name, ""),
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
    
    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")

        return email

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class BaseSkyLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    username_label = "Username"
    username_placeholder = "Enter your username"
    password_placeholder = "Enter your password"

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        self.fields["username"].label = self.username_label
        self.fields["username"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": self.username_placeholder,
                "autofocus": True,
            }
        )

        self.fields["password"].label = "Password"
        self.fields["password"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": self.password_placeholder,
            }
        )

        self.fields["remember_me"].widget.attrs.update(
            {
                "class": "auth-checkbox-input",
            }
        )

    def clean(self):
        login_value = self.cleaned_data.get("username")

        if login_value:
            user = User.objects.filter(email__iexact=login_value).first()

            if user:
                self.cleaned_data["username"] = user.get_username()

        return super().clean()


class MemberLoginForm(BaseSkyLoginForm):
    username_label = "Email Address"
    username_placeholder = "example@sky.com"
    password_placeholder = "#####"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if user.is_staff:
            raise forms.ValidationError(
                "Use the admin login page for this account.",
                code="admin_account",
            )


class AdminLoginForm(BaseSkyLoginForm):
    username_label = "Admin ID"
    username_placeholder = "Enter your admin ID"
    password_placeholder = "#####"
   
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if not user.is_staff:
            raise forms.ValidationError(
                "This account does not have admin access.",
                code="not_admin",
            )

class SkyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email Address"
        self.fields["email"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "example@sky.com",
            }
        )


class SkySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "new_password1": "Create a new password",
            "new_password2": "Confirm your new password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "auth-input",
                    "placeholder": placeholders.get(name, ""),
                }
            )
