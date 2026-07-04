from django.contrib import admin
from .models import ChatKnowledge

@admin.register(ChatKnowledge)
class ChatKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['keywords', 'priority', 'is_active', 'created_at']
    list_filter = ['is_active', 'priority']
    search_fields = ['keywords', 'question_pattern', 'response']
