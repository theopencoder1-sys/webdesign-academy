from django.contrib import admin
from .models import UserStats, LearningGoal

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_xp']

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_type', 'current', 'target']
