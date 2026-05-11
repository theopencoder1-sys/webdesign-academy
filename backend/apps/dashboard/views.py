from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course, Enrollment
from apps.projects.models import Project
from apps.accounts.models import User, UserActivity
from apps.mpesa.models import MpesaPayment

@login_required
def dashboard(request):
    # User stats
    completed_courses = Enrollment.objects.filter(user=request.user, completed=True).count()
    user_projects = Project.objects.filter(user=request.user).count()
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:5]
    payments = MpesaPayment.objects.filter(user=request.user, status='completed').order_by('-created_at')[:3]
    
    context = {
        'completed_courses': completed_courses,
        'user_projects': user_projects,
        'recent_activities': recent_activities,
        'payments': payments,
    }
    return render(request, 'dashboard.html', context)

def admin_stats(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_projects = Project.objects.count()
    total_payments = MpesaPayment.objects.filter(status='completed').count()
    total_revenue = MpesaPayment.objects.filter(status='completed').values('amount')
    revenue_sum = sum(p['amount'] for p in total_revenue) if total_revenue else 0
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_payments = MpesaPayment.objects.filter(status='completed').order_by('-created_at')[:10]
    
    return render(request, 'dashboard/admin_stats.html', {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_projects': total_projects,
        'total_payments': total_payments,
        'revenue_sum': revenue_sum,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
    })
