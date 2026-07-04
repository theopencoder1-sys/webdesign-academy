from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from .models import PageView
from apps.accounts.models import User
from django.db.models import Count, Min, Max

@staff_member_required
def analytics_dashboard(request):
    today = timezone.now().date()
    
    today_views = PageView.objects.filter(created_at__date=today).count()
    today_visitors = PageView.objects.filter(created_at__date=today).values('session_id', 'device_type').distinct().count()
    total_users = User.objects.count()
    
    recent_views = PageView.objects.select_related('user').exclude(user__is_staff=True).exclude(user__is_superuser=True).order_by('-created_at')[:50]
    top_pages = PageView.objects.filter(created_at__date=today).values('page_url').annotate(count=Count('id')).order_by('-count')[:10]
    devices = PageView.objects.filter(created_at__date=today).values('device_type').annotate(count=Count('id'))
    
    last_7_days = []
    for i in range(7):
        d = today - timedelta(days=i)
        count = PageView.objects.filter(created_at__date=d).count()
        last_7_days.append({'date': d.strftime('%a'), 'views': count})
    last_7_days.reverse()
    
    active_today = PageView.objects.filter(created_at__date=today, user__isnull=False).exclude(user__is_staff=True).exclude(user__is_superuser=True).values('user__email', 'user__username').annotate(count=Count('id')).order_by('-count')[:20]
    
    return render(request, 'analytics/dashboard.html', {
        'today_views': today_views,
        'today_visitors': today_visitors,
        'total_users': total_users,
        'recent_views': recent_views,
        'top_pages': top_pages,
        'devices': devices,
        'last_7_days': last_7_days,
        'active_today': active_today,
    })

@staff_member_required
def visitor_log(request):
    # Group by user (or session for anonymous) - show ONE row per person
    from django.db.models.functions import TruncDate
    
    # Get logged-in users grouped
    logged_in = PageView.objects.filter(user__isnull=False, user__is_staff=False, user__is_superuser=False).values(
        'user__email', 'user__username'
    ).annotate(
        first_visit=Min('created_at'),
        last_visit=Max('created_at'),
        page_count=Count('id'),
        device_types=Count('device_type', distinct=True)
    ).order_by('-last_visit')
    
    # Get anonymous visitors grouped by session
    anonymous = PageView.objects.filter(user__isnull=True).values(
        'session_id', 'device_type'
    ).annotate(
        first_visit=Min('created_at'),
        last_visit=Max('created_at'),
        page_count=Count('id')
    ).order_by('-last_visit')[:50]
    
    # Device summary
    device_summary = PageView.objects.values('device_type').annotate(
        count=Count('session_id', 'device_type', distinct=True)
    )
    
    # Total unique visitors
    total_unique = logged_in.count() + anonymous.count()
    
    return render(request, 'analytics/visitors.html', {
        'logged_in': logged_in,
        'anonymous': anonymous,
        'device_summary': device_summary,
        'total_unique': total_unique,
    })
