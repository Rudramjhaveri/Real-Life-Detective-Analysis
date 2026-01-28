from django.core.management.base import BaseCommand
from core.models import Case

class Command(BaseCommand):
    help = 'Seeds the database with initial cases'

    def handle(self, *args, **kwargs):
        cases = [
            {
                'title': 'The Missing Sales',
                'description': 'Analyze the quarterly sales report to find the region with unexplained revenue drops.',
                'difficulty': 'Easy',
                'difficulty_color': 'green',
                'xp_reward': 100
            },
            {
                'title': 'Titanic Survival',
                'description': 'Use the passenger manifest to determine who survived based on ticket class and age.',
                'difficulty': 'Medium',
                'difficulty_color': 'yellow',
                'xp_reward': 250
            },
            {
                'title': 'Housing Market Crash',
                'description': 'Predict the next market correction using historical housing price data.',
                'difficulty': 'Hard',
                'difficulty_color': 'red',
                'xp_reward': 500
            },
        ]

        for case_data in cases:
            Case.objects.get_or_create(title=case_data['title'], defaults=case_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded cases'))
