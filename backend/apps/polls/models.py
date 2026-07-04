from django.db import models
from django.conf import settings
import uuid

class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Leave blank for no expiry')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'polls'
        db_table = 'polls'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.question[:80]
    
    def total_votes(self):
        return sum(option.votes.count() for option in self.options.all())

class PollOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=300)
    
    class Meta:
        app_label = 'polls'
        db_table = 'poll_options'
    
    def __str__(self):
        return f"{self.text[:50]} ({self.vote_count})"
    
    @property
    def vote_count(self):
        return self.votes.count()
    
    @property
    def percentage(self):
        total = self.poll.total_votes()
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100)

class PollVote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'polls'
        db_table = 'poll_votes'
        unique_together = [['option', 'user']]  # One vote per poll per user
    
    def __str__(self):
        return f"{self.user.username} voted for {self.option.text[:30]}"
