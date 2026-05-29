from django.db import models
from django.conf import settings
import uuid

class MentorshipSession(models.Model):
    STATUS = [('pending','Pending'),('confirmed','Confirmed'),('completed','Completed'),('cancelled','Cancelled')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_sessions')
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    session_date = models.DateTimeField()
    meet_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'mentorship_sessions'
        ordering = ['-session_date']
    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.get_status_display()})"

class CodeReview(models.Model):
    STATUS = [('pending','Pending'),('reviewed','Reviewed'),('revision_needed','Revision Needed')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='code_reviews')
    title = models.CharField(max_length=200)
    description = models.TextField()
    code_link = models.URLField(help_text="GitHub repo or code URL")
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'code_reviews'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user.username} - {self.title}"
