from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Case, Submission, UserProfile

class Command(BaseCommand):
    help = 'Simulates a user solving a case to verify XP and Badges'

    def handle(self, *args, **kwargs):
        self.stdout.write("Simulating Case Completion...")

        # 1. Setup User
        user, _ = User.objects.get_or_create(username="player_one", email="p1@example.com")
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
        
        # Reset State
        user.profile.xp = 0
        user.profile.level = 1
        user.profile.badges = []
        user.profile.save()
        Submission.objects.filter(user=user).delete()
        
        self.stdout.write(f" User Reset: XP={user.profile.xp}, Lvl={user.profile.level}")

        # 2. Get Case
        case = Case.objects.first()
        if not case:
            self.stdout.write(self.style.ERROR("No cases found. Run test_auto_case first."))
            return

        # 3. Create Submission (Triggers Signal)
        Submission.objects.create(
            user=user,
            case=case,
            completed=True,
            score=100
        )
        
        # 4. Verify Results
        user.profile.refresh_from_db()
        
        self.stdout.write(f" User Status: XP={user.profile.xp}, Lvl={user.profile.level}")
        self.stdout.write(f" Badges: {user.profile.badges}")

        if user.profile.xp >= case.xp_reward:
             self.stdout.write(self.style.SUCCESS(" [PASS] XP Awarded"))
        else:
             self.stdout.write(self.style.ERROR(" [FAIL] XP not awarded"))

        if 'First Blood' in user.profile.badges:
             self.stdout.write(self.style.SUCCESS(" [PASS] 'First Blood' Badge Awarded"))
        else:
             self.stdout.write(self.style.ERROR(" [FAIL] Badge not awarded"))
