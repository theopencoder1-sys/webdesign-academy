from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def career_roadmap(request):
    return render(request, 'career/roadmap.html')

def resume_templates(request):
    return render(request, 'career/resume.html')

def interview_prep(request):
    return render(request, 'career/interview.html')

def freelancing_guide(request):
    return render(request, 'career/freelance.html')
