from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

# Registration form for custom user
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user