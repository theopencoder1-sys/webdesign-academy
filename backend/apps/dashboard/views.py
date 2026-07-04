from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Enrollment
from apps.projects.models import Project
from apps.accounts.models import User, UserActivity
from apps.mpesa.models import MpesaPayment
from apps.quiz.models import Quiz, Question
from apps.materials.models import CourseMaterial
from apps.polls.models import Poll
import random

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    
    # Courses in progress
    enrollments = Enrollment.objects.filter(user=user, completed=False).select_related('course')[:3]
    
    # Today's challenge - random question
    daily_question = None
    all_questions = Question.objects.filter(quiz__is_published=True)
    if all_questions.exists():
        daily_question = random.choice(all_questions)
    
    # Weekly goal
    week_start = today - timedelta(days=today.weekday())
    lessons_this_week = UserActivity.objects.filter(
        user=user, activity_type='lesson_completed', created_at__date__gte=week_start
    ).count()
    weekly_goal = 5
    weekly_progress = min(100, int((lessons_this_week / weekly_goal) * 100))
    remaining = weekly_goal - lessons_this_week
    if remaining < 0:
        remaining = 0
    
    # Leaderboard
    all_users = list(User.objects.filter(is_active=True).order_by('-xp'))
    user_rank = all_users.index(user) + 1 if user in all_users else 0
    nearby_users = []
    if user in all_users:
        idx = all_users.index(user)
        start = max(0, idx - 1)
        end = min(len(all_users), idx + 3)
        nearby_users = all_users[start:end]
    
    # What's new
    new_materials = CourseMaterial.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    new_polls = Poll.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    
    # Stats
    completed_courses = Enrollment.objects.filter(user=user, completed=True).count()
    user_projects = Project.objects.filter(user=user).count()
    recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:8]
    payments = MpesaPayment.objects.filter(user=user, status='completed').order_by('-created_at')[:3]
    
    return render(request, 'dashboard.html', {
        'enrollments': enrollments,
        'daily_question': daily_question,
        'weekly_progress': weekly_progress,
        'lessons_this_week': lessons_this_week,
        'weekly_goal': weekly_goal,
        'remaining': remaining,
        'user_rank': user_rank,
        'nearby_users': nearby_users,
        'new_materials': new_materials,
        'new_polls': new_polls,
        'completed_courses': completed_courses,
        'user_projects': user_projects,
        'recent_activities': recent_activities,
        'payments': payments,
    })
