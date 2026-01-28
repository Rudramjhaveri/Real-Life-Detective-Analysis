from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Case, Submission

class Command(BaseCommand):
    help = 'Seeds a game state for testing map'

    def handle(self, *args, **kwargs):
        # Create User
        user, created = User.objects.get_or_create(username='gametester')
        user.set_password('gamepass')
        user.email = 'gametester@example.com' # Ensure email for auth
        user.save()
        
        if not hasattr(user, 'profile'):
            from core.models import UserProfile
            UserProfile.objects.create(user=user)

        self.stdout.write(f'User: gametester / gamepass')

        # Ensure Media Directory Exists
        import os
        from django.conf import settings
        from core.models import Dataset

        media_root = settings.MEDIA_ROOT
        datasets_dir = os.path.join(media_root, 'datasets')
        os.makedirs(datasets_dir, exist_ok=True)

        # Create Physical CSV File
        csv_path = os.path.join(datasets_dir, 'titanic_manifest.csv')
        if not os.path.exists(csv_path):
            with open(csv_path, 'w') as f:
                f.write("PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked\n")
                f.write("1,0,3,\"Braund, Mr. Owen Harris\",male,22,1,0,A/5 21171,7.25,,S\n")
                f.write("2,1,1,\"Cumings, Mrs. John Bradley (Florence Briggs Thayer)\",female,38,1,0,PC 17599,71.2833,C85,C\n")
                f.write("3,1,3,\"Heikkinen, Miss. Laina\",female,26,0,0,STON/O2. 3101282,7.925,,S\n")
                f.write("4,1,1,\"Futrelle, Mrs. Jacques Heath (Lily May Peel)\",female,35,1,0,113803,53.1,C123,S\n")
                f.write("5,0,3,\"Allen, Mr. William Henry\",male,35,0,0,373450,8.05,,S\n")
            self.stdout.write(f'Created titanic_manifest.csv at {csv_path}')

        # Create Dataset Record
        ds, created = Dataset.objects.get_or_create(
            name='Titanic Manifest',
            defaults={
                'file': 'datasets/titanic_manifest.csv',
                'description': 'Passenger list from the Titanic disaster.'
            }
        )
        if created:
            self.stdout.write(f'Created Dataset: {ds.name}')

        # Ensure Case 1 points to this dataset
        try:
            c1 = Case.objects.get(id=1)
            c1.dataset = ds
            c1.save()
            self.stdout.write(f'Updated Case 1 with dataset.')
            
            # Create Submission for Case 1 (Correct) - Optional, mainly for map testing
            # Submission.objects.get_or_create(user=user, case=c1, defaults={'is_correct': True}) # Commented to allow testing
        except Case.DoesNotExist:
             self.stdout.write(f'Case 1 not found. Please run migrations or create case first.')

