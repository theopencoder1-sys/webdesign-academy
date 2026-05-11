from django.db import models
import uuid


class Project(models.Model):
    """
    Portfolio projects that users build.
    These are bigger than playground snippets - actual deployed projects.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='projects'
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    long_description = models.TextField(blank=True)
    
    # Project details
    thumbnail = models.ImageField(upload_to='projects/', null=True, blank=True)
    live_url = models.URLField(blank=True, help_text="Deployed project URL")
    github_url = models.URLField(blank=True)
    
    # Tech stack
    technologies = models.JSONField(default=list, help_text="ex: ['HTML', 'CSS', 'JavaScript', 'React']")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Course relation (if it's a course project)
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_projects'
    )
    
    # Portfolio display
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    """
    Multiple screenshots/images for a project.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'project_images'
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.project.title}"


class ProjectReview(models.Model):
    """
    Peer or mentor review of a project.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='project_reviews_given'
    )
    
    # Review
    rating = models.PositiveIntegerField(default=0, help_text="1-5")
    feedback = models.TextField()
    
    # Code review specific
    code_quality = models.PositiveIntegerField(default=0, help_text="1-5")
    design = models.PositiveIntegerField(default=0, help_text="1-5")
    creativity = models.PositiveIntegerField(default=0, help_text="1-5")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_reviews'
        unique_together = ['project', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.project.title} by {self.reviewer.username}"


class ProjectComment(models.Model):
    """
    Comments on a project.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='project_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"