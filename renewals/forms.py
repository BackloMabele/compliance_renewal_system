from django import forms
from django.core.validators import MinValueValidator, validate_email
from django.core.exceptions import ValidationError
from .models import Renewal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser  # Use your custom model
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            validate_email(email)  # Validate email using Django's built-in validator
        except ValidationError:
            raise ValidationError("This email is not valid.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Account is inactive until approved by admin
        if commit:
            user.save()
        return user
    
def validate_email_list(value):
    if not value:
        raise ValidationError("Please provide at least one email address.")
    emails = value.split(',')
    for email in emails:
        try:
            validate_email(email.strip())
        except ValidationError:
            raise ValidationError(f"'{email}' is not a valid email address.")

class RenewalForm(forms.ModelForm):
    notification_emails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter email addresses separated by commas.",
        validators=[validate_email_list]
    )

    class Meta:
        model = Renewal
        fields = ['renewal_title', 'renewal_body', 'issuing_authority', 'issue_date', 'expiration_date', 'notification_period', 'description', 'notification_emails', 'attachment']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }