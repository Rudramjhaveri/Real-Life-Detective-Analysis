from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Seeds a placeholder Google SocialApp to fix DoesNotExist error'

    def handle(self, *args, **kwargs):
        site = Site.objects.get(id=1)
        
        # Check if Google app exists
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google Auth (Placeholder)',
                'client_id': 'PLACEHOLDER_CLIENT_ID',
                'secret': 'PLACEHOLDER_SECRET',
                'key': ''
            }
        )
        
        if created:
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'Created placeholder Google App and linked to {site.domain}'))
        else:
            if site not in app.sites.all():
                app.sites.add(site)
                self.stdout.write(self.style.SUCCESS(f'Linked existing Google App to {site.domain}'))
            else:
                self.stdout.write('Google App already configured')
