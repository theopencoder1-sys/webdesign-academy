from django.contrib import admin
from .models import ForumCategory, ForumTopic, ForumReply, Showcase

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category']

@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ['topic', 'author', 'created_at']

@admin.register(Showcase)
class ShowcaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_featured']
