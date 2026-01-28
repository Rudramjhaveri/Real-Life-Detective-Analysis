from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Case, UserProfile, Submission

def landing(request):
    return render(request, 'core/landing.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'core/login.html')

from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('landing')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'core/register.html')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'core/register.html')

        # Create user (using email as username for simplicity or separate them)
        # User requested "In-Game ID" so maybe username is better? 
        # But form has First/Last/Email/Password. Let's use Email as Username or generate one.
        # Let's check the form in register.html... it DOES rely on fields.
        # I'll use email as username for now to be safe, or just username if the form has it.
        # Checking previous view_file of register.html... Step 716...
        # It has: first_name, last_name, email, password, confirm_password. NO USERNAME field.
        # So I will use email as username.
        
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Create Profile
            UserProfile.objects.create(user=user)
            
            messages.success(request, "Account created! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            
    return render(request, 'core/register.html')

@login_required
def dashboard_view(request):
    # Fetch all cases ordered by ID (progression order)
    all_cases = Case.objects.all().order_by('id')
    
    # Get IDs of cases the user has solved correctly
    solved_ids = set(Submission.objects.filter(
        user=request.user, 
        completed=True
    ).values_list('case_id', flat=True))
    
    cases_with_status = []
    is_next_active = True  # The first case is active by default
    
    for case in all_cases:
        if case.id in solved_ids:
            case.status = 'solved'
            # If current is solved, the next one remains active (pending logic below)
            is_next_active = True 
        elif is_next_active:
            case.status = 'active'
            # We found the active case, subsequent ones should be locked
            is_next_active = False
        else:
            case.status = 'locked'
        
        cases_with_status.append(case)

    return render(request, 'core/dashboard.html', {'cases': cases_with_status})

import pandas as pd
import os

@login_required
def case_detail_view(request, id):
    case = get_object_or_404(Case, id=id)
    
    # Load Dataset
    columns = []
    rows = []
    if case.dataset and case.dataset.file:
        try:
            # Open the file from the storage
            file_path = case.dataset.file.path
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                # handle NaN
                df = df.fillna('')
                columns = df.columns.tolist()
                # Determine "primary key" or ID column for UI (first column usually)
                # Limit rows for initial view to preventing crashing browser
                rows = df.head(100).values.tolist() 
            else:
                 # Fallback for seeded data if path issues (e.g. storage weirdness)
                 columns = ['Error']
                 rows = [['Dataset file not found on server.']]
        except Exception as e:
            columns = ['Error']
            rows = [[str(e)]]
            
    context = {
        'case': case,
        'columns': columns,
        'rows': rows,
    }
    return render(request, 'core/case_detail.html', context)

def solve_view(request, id):
    case = get_object_or_404(Case, id=id)
    return render(request, 'core/solve.html', {'case': case})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .engines.sql_engine import SQLEngine

@login_required
@csrf_exempt # For simplicity in this demo, handling CSRF via template tag locally is better, but this ensures it works for now. 
# Ideally we pass X-CSRFToken in headers. I'll add that to the JS.
def execute_query_view(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            case = get_object_or_404(Case, id=id)

            if not query:
                return JsonResponse({'success': False, 'error': 'No query provided'})

            # Initialize Engine
            if case.dataset and case.dataset.file:
                 engine = SQLEngine(case.dataset.file.path)
                 result = engine.execute_query(query)
                 return JsonResponse(result)
            else:
                 return JsonResponse({'success': False, 'error': 'No dataset found for this case.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@csrf_exempt
def execute_python_view(request, case_id):
    """
    Executes user-submitted Python code with the dataset loaded as 'df'.
    Captures stdout and returns it. Handles errors gracefully.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        case = get_object_or_404(Case, id=case_id)
        
        # Load Dataset
        if not case.dataset:
             return JsonResponse({'success': False, 'error': 'No dataset associated with this case.'})
             
        file_path = case.dataset.file.path
        if not os.path.exists(file_path):
             return JsonResponse({'success': False, 'error': 'Dataset file not found.'})

        # Context for execution
        import pandas as pd
        import io
        import sys
        
        # Load df
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
             return JsonResponse({'success': False, 'error': f'Failed to load CSV: {str(e)}'})

        # Capture Stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Restricted Environment (Safe-ish for local dev, not prod)
        # We allow pandas as 'pd' and 'df'
        local_scope = {
            'pd': pd,
            'df': df
        }
        
        try:
            # Execute User Code
            exec(code, {}, local_scope)
            output = redirected_output.getvalue()
            success = True
            error_message = None

            # Validation Logic
            is_correct = False
            validation_message = ""
            
            # Find the active Python question for this case (assuming 1 per case for prototype)
            # In a real app, we'd pass question_id from frontend
            question = case.questions.filter(question_type='PYTHON').first()
            
            if question and question.validation_query:
                # Run Validation Code (Expected Result)
                # We expect the validation code to produce an output or define a variable 'expected_result'
                # For this prototype, let's assume we compare STDOUT equality
                
                # Capture Expected Output
                expected_output_io = io.StringIO()
                sys.stdout = expected_output_io
                
                validation_scope = {'pd': pd, 'df': df} # Clean scope
                exec(question.validation_query, {}, validation_scope)
                expected_output = expected_output_io.getvalue()
                
                # Restore Stdout for final return
                sys.stdout = old_stdout
                
                # Compare
                if output.strip() == expected_output.strip():
                    is_correct = True
                    validation_message = "Correct! Task Completed."
                else:
                    validation_message = "Incorrect output."
            elif question:
                 # If no validation query but question exists, maybe just running it is enough?
                 # ideally we should have a validation query.
                 pass

        except Exception as e:
            # Capture the full traceback or just the error message
            import traceback
            success = False
            output = redirected_output.getvalue() # Get partially printed lines if any
            error_message = traceback.format_exc()
            is_correct = False
            validation_message = "Execution Error"
        finally:
            sys.stdout = old_stdout

        return JsonResponse({
            'success': success,
            'output': output if success else output, # Send output even on fail (partial logs)
            'error': error_message,
            'is_correct': is_correct,
            'validation_message': validation_message
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Server Error: {str(e)}"})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def result_view(request):
    return render(request, 'core/result.html')


def leaderboard_view(request):
    return render(request, 'core/leaderboard.html')

@user_passes_test(lambda u: u.is_authenticated)
def profile_view(request):
    if request.method == 'POST':
        if 'avatar' in request.FILES:
            request.user.profile.avatar = request.FILES['avatar']
            request.user.profile.save()
    return render(request, 'core/profile.html')

@login_required
def admin_dashboard_view(request):
    if not request.user.is_staff:
        messages.error(request, "Access Denied: Admin privileges required.")
        return redirect('dashboard')
    total_users = User.objects.count()
    total_submissions = Submission.objects.count()
    active_today = User.objects.filter(last_login__date=timezone.now().date()).count()
    total_cases_solved = Submission.objects.filter(completed=True).count()
    profiles = UserProfile.objects.select_related('user').all()[:20]

    context = {
        'total_users': total_users,
        'total_submissions': total_submissions,
        'active_today': active_today,
        'total_cases_solved': total_cases_solved,
        'profiles': profiles,
    }
    return render(request, 'core/admin_dashboard.html', context)
