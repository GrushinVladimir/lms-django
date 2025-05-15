# lms_cleint/management/commands/setup_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group as AuthGroup

class Command(BaseCommand):
    help = 'Sets up initial auth groups for the e-learning system'

    def handle(self, *args, **kwargs):
        # Delete default Django groups
        AuthGroup.objects.exclude(name__in=['students', 'prepodavatels']).delete()

        # Create or get auth groups
        AuthGroup.objects.get_or_create(name='students')
        AuthGroup.objects.get_or_create(name='prepodavatels')

        self.stdout.write(self.style.SUCCESS('Successfully set up auth groups'))