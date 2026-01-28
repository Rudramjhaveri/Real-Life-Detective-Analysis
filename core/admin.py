from django.contrib import admin
from .models import UserProfile, Dataset, Case, Question, Submission, QuestionAttempt

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp')

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'xp_reward', 'is_active')
    inlines = [QuestionInline]

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'case', 'completed', 'score', 'submitted_at')

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'attempted_at')
