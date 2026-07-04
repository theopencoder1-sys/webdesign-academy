from django.db import models
import uuid

class ChatKnowledge(models.Model):
    """Question-Answer knowledge base for chatbot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keywords = models.CharField(max_length=500, help_text="Comma-separated keywords that trigger this response")
    question_pattern = models.TextField(help_text="Example questions this matches")
    response = models.TextField(help_text="The bot's response")
    priority = models.IntegerField(default=1, help_text="Higher = checked first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'chatbot'
        db_table = 'chat_knowledge'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.keywords[:80]
