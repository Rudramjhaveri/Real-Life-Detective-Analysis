from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Fixes Site configuration and ensures UserProfiles exist'

    def handle(self, *args, **kwargs):
        # 1. Fix Site
        site, created = Site.objects.get_or_create(id=1)
        site.domain = '127.0.0.1:8000'
        site.name = 'Real-Life Data Detective'
        site.save()
        self.stdout.write(f'Updated Site ID 1: {site.domain}')

        # 2. Fix Missing Profiles
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(f'Created missing profile for {user.username}')
            else:
                self.stdout.write(f'Profile exists for {user.username}')
