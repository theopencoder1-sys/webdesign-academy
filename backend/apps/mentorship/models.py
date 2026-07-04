from django.db import models
from django.conf import settings
import uuid

class MentorshipSession(models.Model):
    STATUS = [('pending','Pending Approval'),('approved','Approved'),('completed','Completed'),('cancelled','Cancelled'),('rejected','Rejected')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_sessions')
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    session_date = models.DateTimeField()
    meet_link = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = 'mentorship'
        db_table = 'mentorship_sessions'
        ordering = ['-session_date']
    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.get_status_display()})"

class Availability(models.Model):
    DAYS = [(0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_sessions = models.PositiveIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    class Meta:
        app_label = 'mentorship'
        db_table = 'mentorship_availability'
        ordering = ['day', 'start_time']
    def __str__(self):
        return f"{self.get_day_display()} {self.start_time}-{self.end_time}"

class CodeReview(models.Model):
    STATUS = [('pending','Pending'),('reviewed','Reviewed'),('revision_needed','Revision Needed')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='code_reviews')
    title = models.CharField(max_length=200)
    description = models.TextField()
    code_link = models.URLField()
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = 'mentorship'
        db_table = 'code_reviews'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.user.username} - {self.title}"
