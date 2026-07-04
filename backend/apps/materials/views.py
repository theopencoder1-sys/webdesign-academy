from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import CourseMaterial
from apps.courses.models import Course

def course_materials(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    materials = CourseMaterial.objects.filter(course=course, is_published=True)
    return render(request, 'materials/list.html', {
        'course': course,
        'materials': materials
    })

@staff_member_required
def upload_material(request):
    courses = Course.objects.all()
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type')
        video_url = request.POST.get('video_url', '')
        file = request.FILES.get('file')
        
        if title and course_id:
            course = Course.objects.get(id=course_id)
            CourseMaterial.objects.create(
                course=course,
                title=title,
                description=description,
                material_type=material_type,
                video_url=video_url,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, f'Material "{title}" uploaded successfully!')
            return redirect('upload_material')
    
    return render(request, 'materials/upload.html', {'courses': courses})

from django.http import JsonResponse
from .models import CourseMaterial
from apps.courses.models import Course

def materials_api(request, course_slug):
    try:
        course = Course.objects.get(slug=course_slug)
        materials = CourseMaterial.objects.filter(course=course, is_published=True)
        data = []
        for m in materials:
            data.append({
                'title': m.title,
                'type': m.material_type,
                'file_url': m.file.url if m.file else None,
                'video_url': m.video_url if m.video_url else None,
            })
        return JsonResponse({'materials': data})
    except Course.DoesNotExist:
        return JsonResponse({'materials': []})
