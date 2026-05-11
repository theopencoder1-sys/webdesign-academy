from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, ProjectImage, ProjectComment
from django.utils.text import slugify

def project_list(request):
    projects = Project.objects.filter(status='published').order_by('-created_at')
    return render(request, 'projects/list.html', {'projects': projects})

@login_required
def my_projects(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/my_projects.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        live_url = request.POST.get('live_url', '')
        github_url = request.POST.get('github_url', '')
        technologies = request.POST.get('technologies', '')
        
        project = Project.objects.create(
            user=request.user,
            title=title,
            slug=slugify(title),
            description=description,
            live_url=live_url,
            github_url=github_url,
            technologies=[t.strip() for t in technologies.split(',')],
            status='published'
        )
        messages.success(request, 'Project published! 🎉')
        return redirect('project_detail', slug=project.slug)
    
    return render(request, 'projects/create.html')

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    comments = project.comments.all()
    return render(request, 'projects/detail.html', {
        'project': project,
        'comments': comments
    })

@login_required
def add_comment(request, slug):
    if request.method == 'POST':
        project = get_object_or_404(Project, slug=slug)
        content = request.POST.get('content')
        ProjectComment.objects.create(
            project=project,
            user=request.user,
            content=content
        )
    return redirect('project_detail', slug=slug)
