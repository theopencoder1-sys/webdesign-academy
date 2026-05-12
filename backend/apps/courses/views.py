from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson, Enrollment
from apps.progress.models import UserCourseProgress
import datetime

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'course_list.html')

def html_full(request):
    return render(request, 'courses/html_full.html')

def css_full(request):
    return render(request, 'courses/css_full.html')

def javascript_full(request):
    return render(request, 'courses/javascript_full.html')

@login_required
def tailwind_full(request):
    # STRICTLY premium only - no exceptions
    if not request.user.is_premium:
        messages.error(request, 'This is a premium course. Upgrade to PRO to access!')
        return redirect('pricing')
    return render(request, 'courses/tailwind_full.html')

def lesson_detail(request, course_slug, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug, module__course__slug=course_slug, is_published=True)
    return render(request, 'lesson_detail.html', {'lesson': lesson})

@login_required
def certificate(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    user = request.user
    
    if not user.is_premium and not user.is_staff:
        messages.error(request, 'You need a PRO subscription to get certificates!')
        return redirect('pricing')
    
    progress = UserCourseProgress.objects.filter(user=user, course=course, completed=True).first()
    enrollment = Enrollment.objects.filter(user=user, course=course, completed=True).first()
    
    if not progress and not enrollment and not user.is_staff:
        messages.error(request, f'Complete "{course.title}" first to get the certificate.')
        return redirect('dashboard')
    
    today = datetime.date.today()
    cert_id = f"WD-{course.slug[:4].upper()}-{user.id}-{today.strftime('%Y%m%d')}"
    
    return render(request, 'courses/certificate.html', {
        'user': user,
        'course': course,
        'date': today,
        'cert_id': cert_id
    })

@login_required
def fullstack_full(request):
    if not request.user.is_premium:
        return render(request, 'courses/premium_gate.html', {'course': 'Full-Stack Developer'})
    return render(request, 'courses/pro/fullstack.html')

@login_required
def python_full(request):
    if not request.user.is_premium:
        return render(request, 'courses/premium_gate.html', {'course': 'Python Programming'})
    return render(request, 'courses/pro/python.html')

@login_required
def react_full(request):
    if not request.user.is_premium:
        return render(request, 'courses/premium_gate.html', {'course': 'React.js Masterclass'})
    return render(request, 'courses/pro/react.html')

@login_required
def uiux_full(request):
    if not request.user.is_premium:
        return render(request, 'courses/premium_gate.html', {'course': 'UI/UX Design'})
    return render(request, 'courses/pro/uiux.html')

@login_required
def cybersecurity_full(request):
    if not request.user.is_premium:
        return render(request, 'courses/premium_gate.html', {'course': 'Cybersecurity'})
    return render(request, 'courses/pro/cybersecurity.html')
