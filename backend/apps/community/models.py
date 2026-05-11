from django.db import models
import uuid


class ForumCategory(models.Model):
    """
    Categories for community forum.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#6366f1')
    order = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'forum_categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'Forum categories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def topic_count(self):
        return self.topics.count()


class ForumTopic(models.Model):
    """
    Discussion topics in the forum.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='forum_topics')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    view_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_topics'
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"


class ForumReply(models.Model):
    """
    Replies to forum topics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='forum_replies')
    
    content = models.TextField()
    
    is_solution = models.BooleanField(default=False, help_text="Marked as solution by topic author")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'forum_replies'
        ordering = ['created_at']
        verbose_name_plural = 'Forum replies'
    
    def __str__(self):
        return f"Reply by {self.author.username} in {self.topic.title}"


class Showcase(models.Model):
    """
    Community project showcase - featured student work.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='showcases')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='showcases')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    lessons_learned = models.TextField(blank=True)
    
    is_featured = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'showcases'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"Showcase: {self.title}"