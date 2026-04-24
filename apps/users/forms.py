# Authors: w2143865

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

User = get_user_model()


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


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class MemberLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = "Email Address"
        self.fields["username"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "example@sky.com",
                "autofocus": True,
            }
        )
        self.fields["password"].label = "Password"
        self.fields["password"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "#####",
            }
        )
        self.fields["remember_me"].widget.attrs.update({"class": "auth-checkbox-input"})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_staff:
            raise forms.ValidationError(
                "Please use the admin login page for this account.",
                code="admin_account",
            )


class AdminLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].label = "Admin ID"
        self.fields["username"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "Enter your admin ID",
                "autofocus": True,
            }
        )
        self.fields["password"].label = "Password"
        self.fields["password"].widget.attrs.update(
            {
                "class": "auth-input",
                "placeholder": "#####",
            }
        )
        self.fields["remember_me"].widget.attrs.update({"class": "auth-checkbox-input"})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Please use the member login page for this account.",
                code="not_admin_account",
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
