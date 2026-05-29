from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MentorshipSession, CodeReview

@login_required
def mentorship_hub(request):
    if not request.user.is_premium:
        messages.error(request, 'Mentorship is for PRO members only! Upgrade now.')
        return redirect('pricing')
    sessions = MentorshipSession.objects.filter(user=request.user).order_by('-session_date')[:10]
    reviews = CodeReview.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'mentorship/hub.html', {'sessions': sessions, 'reviews': reviews})

@login_required
def book_session(request):
    if not request.user.is_premium:
        return redirect('pricing')
    if request.method == 'POST':
        topic = request.POST.get('topic')
        description = request.POST.get('description')
        date = request.POST.get('session_date')
        if topic and date:
            MentorshipSession.objects.create(user=request.user, topic=topic, description=description, session_date=date)
            messages.success(request, 'Session booked! You will receive a confirmation email with the meeting link.')
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
            messages.success(request, 'Code submitted for review! Dancan will review it within 48 hours.')
        return redirect('mentorship_hub')
    return render(request, 'mentorship/submit_review.html')
