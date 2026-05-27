from django.shortcuts import render
from django.db.models import Q
from .models import Course, Lesson
from apps.projects.models import Project

def search(request):
    query = request.GET.get('q', '').strip()
    results = {'courses': [], 'lessons': [], 'projects': []}
    
    if query:
        results['courses'] = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_published=True
        )[:10]
        
        results['lessons'] = Lesson.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_published=True
        )[:10]
        
        results['projects'] = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status='published'
        )[:5]
    
    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'total': len(results['courses']) + len(results['lessons']) + len(results['projects'])
    })
