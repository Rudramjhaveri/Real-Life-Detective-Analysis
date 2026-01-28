from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Dataset, Case, Question
import pandas as pd
import os

@receiver(post_save, sender=Dataset)
def auto_generate_case(sender, instance, created, **kwargs):
    """
    When a Dataset is uploaded:
    1. Parse CSV key metadata (columns, rows).
    2. Create a generic Case wrapper if one doesn't exist.
    3. Generate 2-3 standard 'Observation' questions.
    """
    if created and instance.file:
        try:
            # 1. Parse CSV
            file_path = instance.file.path
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                # Save Metadata
                columns = df.columns.tolist()
                row_count = len(df)
                instance.columns_metadata = {
                    "columns": columns,
                    "row_count": row_count,
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
                }
                instance.save(update_fields=['columns_metadata'])

                # 2. Create Case
                # Check if case exists for this dataset to avoid dupes on re-save
                if not Case.objects.filter(dataset=instance).exists():
                    case = Case.objects.create(
                        title=f"Investigation: {instance.name}",
                        dataset=instance,
                        description=f"A new dataset has been secured from {instance.name}. Your mission is to explore the data, verify its integrity, and report initial findings.\n\n**Data Overview**:\n- Rows: {row_count}\n- Columns: {', '.join(columns[:5])}...",
                        difficulty='Easy',
                        xp_reward=100,
                        order=Case.objects.count() + 1
                    )

                    # 3. Create Default Questions
                    
                    # Q1: Row Count Check (SQL)
                    Question.objects.create(
                        case=case,
                        text=f"How many records are in the dataset?",
                        question_type='SQL',
                        points=20,
                        validation_query=f"SELECT COUNT(*) FROM dataset",
                        order=1
                    )
                    
                    # Q2: First Column Check (Python)
                    first_col = columns[0]
                    Question.objects.create(
                        case=case,
                        text=f"What is the name of the first column?",
                        question_type='INSIGHT', # Insight map be better for simple string match
                        correct_answer=first_col,
                        points=30,
                        order=2
                    )

        except Exception as e:
            print(f"Error auto-generating case: {e}")

from .models import Submission
@receiver(post_save, sender=Submission)
def award_xp_on_submission(sender, instance, created, **kwargs):
    """
    When a user completes a case (Submission.completed=True), award the Case's XP reward.
    """
    if instance.completed and instance.case:
        # Check if already awarded (simple check: if updated recently? Or just trust flag)
        # Ideally we'd have a 'rewarded' flag on Submission to prevent double counting on multiple saves
        # For prototype, we assume 'completed' flips once.
        
        profile = instance.user.profile
        reward = instance.case.xp_reward
        
        # Add XP
        profile.xp += reward
        
        # Check Level Up
        new_level = profile.calculate_level()
        if new_level > profile.level:
            profile.level = new_level
            
        # Check Badges
        solved_count = Submission.objects.filter(user=instance.user, completed=True).count()
        
        if solved_count == 1 and 'First Blood' not in profile.badges:
             profile.badges.append('First Blood')
        elif solved_count >= 5 and 'Veteran' not in profile.badges:
             profile.badges.append('Veteran')

        profile.save()
