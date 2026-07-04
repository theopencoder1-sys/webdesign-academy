from django.db import models
from django.conf import settings
import uuid

class PageView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.CharField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    device_type = models.CharField(max_length=20, blank=True)  # mobile, tablet, desktop
    session_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'analytics'
        db_table = 'analytics_pageviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['page_url']),
        ]
    
    def __str__(self):
        return f"{self.user or 'Anonymous'} → {self.page_url} at {self.created_at.strftime('%H:%M')}"

class DailyStats(models.Model):
    date = models.DateField(unique=True)
    total_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_signups = models.PositiveIntegerField(default=0)
    most_viewed_page = models.CharField(max_length=500, blank=True)
    
    class Meta:
        app_label = 'analytics'
        db_table = 'analytics_dailystats'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.total_views} views"
