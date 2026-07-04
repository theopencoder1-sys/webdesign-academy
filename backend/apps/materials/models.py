from django.db import models
from django.conf import settings
import uuid

class CourseMaterial(models.Model):
    MATERIAL_TYPES = [
        ('pdf', 'PDF Document'),
        ('video', 'Video Link'),
        ('code', 'Source Code'),
        ('slides', 'Presentation Slides'),
        ('exercise', 'Exercise File'),
        ('cheatsheet', 'Cheat Sheet'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='pdf')
    file = models.FileField(upload_to='materials/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or video link")
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'materials'
        db_table = 'course_materials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
