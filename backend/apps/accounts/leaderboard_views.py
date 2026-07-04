from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import User

def leaderboard(request):
    # Get filter
    filter_type = request.GET.get('filter', 'all')  # all, today, week, month
    
    users = User.objects.filter(is_active=True)
    
    if filter_type == 'today':
        users = users.filter(last_active__date=timezone.now().date())
    elif filter_type == 'week':
        users = users.filter(last_active__date__gte=timezone.now().date() - timedelta(days=7))
    elif filter_type == 'month':
        users = users.filter(last_active__date__gte=timezone.now().date() - timedelta(days=30))
    
    top_learners = users.order_by('-xp')[:50]
    
    return render(request, 'leaderboard.html', {
        'top_learners': top_learners,
        'filter': filter_type
    })
