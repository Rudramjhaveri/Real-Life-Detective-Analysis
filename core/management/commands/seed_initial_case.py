from django.core.management.base import BaseCommand
from core.models import Case, Dataset, Question
from django.core.files.base import ContentFile
import json

class Command(BaseCommand):
    help = 'Seeds the database with an initial demo case (Titanic)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding initial data...')

        # 1. Create Dummy Dataset
        if not Dataset.objects.filter(name='Titanic Passenger List').exists():
            dataset = Dataset.objects.create(
                name='Titanic Passenger List',
                description='The famous Titanic dataset containing passenger details.',
                columns_metadata={"PassengerId": "int", "Survived": "int", "Pclass": "int", "Name": "str", "Sex": "str", "Age": "float", "Fare": "float"}
            )
            # Create a dummy CSV file content
            dummy_csv = "PassengerId,Survived,Pclass,Name,Sex,Age,Fare\n1,0,3,Mr. Owen Harris,male,22,7.25\n2,1,1,Mrs. John Bradley,female,38,71.28"
            dataset.file.save('titanic.csv', ContentFile(dummy_csv))
            self.stdout.write(self.style.SUCCESS('Created Titanic Dataset.'))
        else:
            dataset = Dataset.objects.get(name='Titanic Passenger List')

        # 2. Create Case 1: Titanic Mystery
        if not Case.objects.filter(title='The Unsinkable Ship?').exists():
            case = Case.objects.create(
                title='The Unsinkable Ship?',
                description='Analyze the passenger list of the RMS Titanic. Discover who survived and why. Your mission is to uncover the patterns of survival.',
                difficulty='Easy',
                difficulty_color='green',
                xp_reward=150,
                dataset=dataset,
                order=1
            )
            
            # 3. Create Questions
            Question.objects.create(
                case=case,
                text='How many passengers are in this dataset?',
                question_type='SQL',
                validation_query='SELECT COUNT(*) FROM dataset',
                order=1,
                points=10
            )
            Question.objects.create(
                case=case,
                text='What is the average fare paid by passengers?',
                question_type='PYTHON',
                validation_query='df["Fare"].mean()',
                order=2,
                points=20
            )
            
            self.stdout.write(self.style.SUCCESS('Created Case: The Unsinkable Ship?'))
        else:
            self.stdout.write('Case already exists.')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
