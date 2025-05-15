"""Forms for the Knowledge Learning application.

This module contains forms for user registration.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

class RegistrationForm(UserCreationForm):
    """Form for user registration with email.

    Extends Django's UserCreationForm to include an email field and custom save logic.

    Attributes:
        email (EmailField): User's email address (required).
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """Save the user with email and set as inactive.

        Args:
            commit (bool): Whether to save the user to the database (default: True).

        Returns:
            Utilisateur: The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user