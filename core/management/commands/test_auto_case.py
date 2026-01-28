from django.core.management.base import BaseCommand
from core.models import Dataset
from django.core.files.base import ContentFile
import os

class Command(BaseCommand):
    help = 'Simulates a file upload to trigger the auto-case signal'

    def handle(self, *args, **kwargs):
        self.stdout.write("Simulating CSV Upload...")
        
        # Create a dummy CSV content
        csv_content = b"id,name,role,salary\n1,Alice,Engineer,90000\n2,Bob,Designer,85000\n3,Charlie,Manager,120000\n4,David,Intern,30000"
        
        # Create Dataset
        # This save() should trigger the post_save signal
        ds = Dataset(name="HR Payroll Data")
        ds.file.save("hr_payroll.csv", ContentFile(csv_content))
        ds.save()
        
        self.stdout.write(self.style.SUCCESS(f"Dataset '{ds.name}' created!"))
        
        # Check if Case was created
        from core.models import Case
        case = Case.objects.filter(dataset=ds).first()
        
        if case:
            self.stdout.write(self.style.SUCCESS(f" [PASS] Auto-Case Created: {case.title}"))
            self.stdout.write(f" Description Preview: {case.description[:50]}...")
            
            # Check Questions
            questions = case.questions.all()
            self.stdout.write(f" [PASS] Generated {questions.count()} Questions:")
            for q in questions:
                 self.stdout.write(f"  - [{q.question_type}] {q.text}")
        else:
            self.stdout.write(self.style.ERROR(" [FAIL] Case was not automatically generated."))
