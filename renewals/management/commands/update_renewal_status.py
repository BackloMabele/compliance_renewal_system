from django.core.management.base import BaseCommand
from renewals.models import Renewal

class Command(BaseCommand):
    help = "Update renewal statuses based on expiration dates and notification periods"

    def handle(self, *args, **kwargs):
        renewals = Renewal.objects.all()
        for renewal in renewals:
            renewal.update_status()  # Calls update_status method from models.py
        self.stdout.write(self.style.SUCCESS('Successfully updated renewal statuses'))
