from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates initial user groups'

    def handle(self, *args, **options):
        Group.objects.get_or_create(name='Преподаватель')
        Group.objects.get_or_create(name='Студент')
        self.stdout.write(self.style.SUCCESS('Successfully created user groups'))