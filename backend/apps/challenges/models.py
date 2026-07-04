from django.db import models
from django.conf import settings
import uuid

class DailyChallenge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, default='beginner')
    topic = models.CharField(max_length=50)  # html, css, js
    starter_code = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=10)
    date = models.DateField(unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'challenges'
        db_table = 'daily_challenges'
        ordering = ['-date']
    
    def __str__(self):
        return f"[{self.date}] {self.title}"

class ChallengeSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    code = models.TextField()
    score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'challenges'
        db_table = 'daily_challenge_submissions'
        unique_together = ['user', 'challenge']
