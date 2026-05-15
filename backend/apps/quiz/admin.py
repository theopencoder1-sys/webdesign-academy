from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'question_count', 'passing_score', 'is_published']
    list_filter = ['difficulty', 'is_published']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'order']
    inlines = [ChoiceInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'percentage', 'passed', 'completed_at']
    list_filter = ['passed', 'quiz']
