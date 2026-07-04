from django.contrib import admin
from .models import CourseMaterial

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'is_published', 'download_count', 'created_at']
    list_filter = ['material_type', 'course', 'is_published']
    search_fields = ['title', 'description']
