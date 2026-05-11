from django.contrib import admin
from .models import PlaygroundSnippet, PlaygroundTemplate, CodeChallenge

@admin.register(PlaygroundSnippet)
class PlaygroundSnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status']

@admin.register(PlaygroundTemplate)
class PlaygroundTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty']

@admin.register(CodeChallenge)
class CodeChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'xp_reward']
