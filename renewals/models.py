from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import FileExtensionValidator
from datetime import date

# Define CustomUser properly
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Email should be unique
    is_approved = models.BooleanField(default=False)  # Field for approval status

class Renewal(models.Model):
    RENEWAL_STATUS = [
        ('active', 'Active'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
    ]
    
    attachment = models.FileField(
        upload_to='renewal_attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'])]
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Reference CustomUser
    renewal_title = models.CharField(max_length=255)
    renewal_body = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiration_date = models.DateField()
    notification_period = models.IntegerField()
    status = models.CharField(max_length=20, choices=RENEWAL_STATUS, default='active')
    description = models.TextField(blank=True, null=True)
    notification_emails = models.TextField(blank=True, null=True)

    @property
    def days_remaining(self):
        """Calculate days left before expiry."""
        return (self.expiration_date - date.today()).days

    def update_status(self, save=True):
        """Update the status based on expiration date and notification period."""
        days_left = self.days_remaining

        if days_left <= 0:
            new_status = 'expired'
        elif days_left <= self.notification_period:
            new_status = 'expiring_soon'
        else:
            new_status = 'active'

        if self.status != new_status:
            self.status = new_status
            if save:
                super().save(update_fields=['status'])

    def save(self, *args, **kwargs):
        """Override save method to update status before saving."""
        self.update_status(save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.renewal_title} (Expires: {self.expiration_date})"
