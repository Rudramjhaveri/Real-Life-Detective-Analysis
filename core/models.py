from django.db import models
from django.contrib.auth.models import User
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    badges = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Lvl {self.level}"

    def calculate_level(self):
        """Simple Logic: Level = 1 + (XP // 100)"""
        return 1 + (self.xp // 100)
    
    @property
    def next_level_xp(self):
        """XP needed for next level"""
        return self.level * 100
        
    @property
    def progress_percent(self):
        """Percentage to next level for UI bar"""
        current_level_base = (self.level - 1) * 100
        return ((self.xp - current_level_base) / 100) * 100

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='datasets/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Store CSV columns metadata (names, types) for validation/UI
    columns_metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

class Case(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    COLOR_CHOICES = [
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
    ]

    title = models.CharField(max_length=200)
    # The 'story' - Rich text description of the scenario
    description = models.TextField() 
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases')
    
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    difficulty_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='green')
    xp_reward = models.IntegerField(default=100)
    
    order = models.IntegerField(default=0, help_text="Order in the learning path")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    TYPE_CHOICES = [
        ('SQL', 'SQL Query'),
        ('PYTHON', 'Python/Pandas'),
        ('MCQ', 'Multiple Choice'),
        ('INSIGHT', 'Data Insight (Text)'),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="The question/task for the user")
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.IntegerField(default=0)
    
    # For MCQ
    options = models.JSONField(default=list, blank=True, null=True, help_text="List of options for MCQ. Example: [\"Option A\", \"Option B\"]")
    
    # Validation
    correct_answer = models.TextField(blank=True, help_text="Exact answer for MCQ/Insight")
    validation_query = models.TextField(blank=True, help_text="SQL/Python code to generate the correct result")
    
    points = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.case.title} - Q{self.order}: {self.question_type}"

class Submission(models.Model):
    """Tracks the completion status of the entire Case"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.case.title}"

class QuestionAttempt(models.Model):
    """Tracks attempts on individual questions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    users_code = models.TextField(blank=True, help_text="The SQL/Python code user wrote")
    is_correct = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question}"
