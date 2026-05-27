from django.db import models
from django.conf import settings
import uuid

class Quiz(models.Model):
    DIFFICULTY = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY, default='beginner')
    passing_score = models.PositiveIntegerField(default=70)
    time_limit_minutes = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'quiz'
        db_table = 'quizzes'
        ordering = ['order', 'created_at']
    def __str__(self): return self.title
    @property
    def question_count(self): return self.questions.count()

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        app_label = 'quiz'
        db_table = 'questions'
        ordering = ['order']
    def __str__(self): return self.text[:80]

class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    class Meta:
        app_label = 'quiz'
        db_table = 'choices'
    def __str__(self): return f"{self.text[:50]}"

class QuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = 'quiz'
        db_table = 'quiz_attempts'
        ordering = ['-completed_at']
    def __str__(self): return f"{self.user.username} - {self.quiz.title}"
    @property
    def percentage(self):
        if self.total_questions == 0: return 0
        return round((self.correct_answers / self.total_questions) * 100)
