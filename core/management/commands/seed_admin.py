from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Seeds a test admin user and ensures Site ID 1 exists'

    def handle(self, *args, **kwargs):
        # Ensure Site ID 1 is localhost
        site, created = Site.objects.get_or_create(id=1)
        site.domain = '127.0.0.1:8000'
        site.name = 'Real-Life Data Detective'
        site.save()
        self.stdout.write(f'Updated Site ID 1: {site.domain}')

        # Create Test Admin
        if not User.objects.filter(username='testadmin').exists():
            User.objects.create_superuser('testadmin', 'admin@test.com', 'testpass123')
            self.stdout.write(self.style.SUCCESS('Created superuser: testadmin / testpass123'))
        else:
            self.stdout.write('Superuser testadmin already exists')
