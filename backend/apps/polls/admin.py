from django.contrib import admin
from .models import Poll, PollOption, PollVote

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 3

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_by', 'is_active', 'total_votes', 'created_at']
    inlines = [PollOptionInline]

@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'created_at']
