from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MentorshipSession, Availability, CodeReview
from datetime import datetime, timedelta

@login_required
def mentorship_hub(request):
    if not request.user.is_premium:
        messages.error(request, 'Mentorship is for PRO members only!')
        return redirect('pricing')
    
    sessions = MentorshipSession.objects.filter(user=request.user).order_by('-session_date')[:10]
    availability = Availability.objects.filter(is_active=True).order_by('day')
    
    # Check if any slots are fully booked
    booked_slots = {}
    for avail in availability:
        booked_count = MentorshipSession.objects.filter(
            session_date__week_day=avail.day + 1,
            status='approved'
        ).count()
        booked_slots[avail.id] = booked_count >= avail.max_sessions
    
    return render(request, 'mentorship/hub.html', {
        'sessions': sessions,
        'availability': availability,
        'booked_slots': booked_slots
    })

@login_required
def book_session(request):
    if not request.user.is_premium:
        return redirect('pricing')
    
    if request.method == 'POST':
        topic = request.POST.get('topic')
        description = request.POST.get('description')
        date_str = request.POST.get('session_date')
        
        if topic and date_str:
            session_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            
            # Check if slot is available
            day_of_week = session_date.weekday()
            avail = Availability.objects.filter(day=day_of_week, is_active=True).first()
            
            if avail:
                booked_count = MentorshipSession.objects.filter(
                    session_date__date=session_date.date(),
                    status='approved'
                ).count()
                
                if booked_count >= avail.max_sessions:
                    messages.error(request, 'This time slot is fully booked. Please choose another time.')
                    return redirect('mentorship_hub')
            
            session = MentorshipSession.objects.create(
                user=request.user,
                topic=topic,
                description=description,
                session_date=session_date
            )
            
            # Send email to Dancan
            try:
                send_mail(
                    subject=f'New Mentorship Request: {topic}',
                    message=f'''New mentorship session request!

From: {request.user.username} ({request.user.email})
Topic: {topic}
Date: {session_date.strftime('%B %d, %Y at %I:%M %p')}
Description: {description}

Approve or reject: https://dancoder1.pythonanywhere.com/admin/mentorship/mentorshipsession/{session.id}/change/''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['theopencoder1@gmail.com'],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, '✅ Session requested! You will receive an email when Dancan approves it.')
            return redirect('mentorship_hub')
    
    return render(request, 'mentorship/book.html')

@login_required
def submit_review(request):
    if not request.user.is_premium:
        return redirect('pricing')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        code_link = request.POST.get('code_link')
        if title and code_link:
            CodeReview.objects.create(user=request.user, title=title, description=description, code_link=code_link)
            messages.success(request, 'Code submitted! Dancan will review within 48 hours.')
        return redirect('mentorship_hub')
    return render(request, 'mentorship/submit_review.html')
