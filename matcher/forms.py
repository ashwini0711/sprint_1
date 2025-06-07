from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# RegistrationForm for user sign-up, extends Django's ModelForm for User model
class RegistrationForm(forms.ModelForm):
    # Password field with password input widget to hide input text
    password = forms.CharField(widget=forms.PasswordInput)
    # Role selection field with choices from UserProfile model roles
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        # Use Django's built-in User model for the form
        model = User
        # Include only these fields in the registration form
        fields = ['username', 'email','password']