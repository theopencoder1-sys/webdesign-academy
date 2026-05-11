from django.db import models
import uuid


class PlaygroundSnippet(models.Model):
    """
    Saved code snippets in the playground.
    Users can save HTML/CSS/JS experiments.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='playground_snippets'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Code storage
    html_code = models.TextField(blank=True, default='')
    css_code = models.TextField(blank=True, default='')
    js_code = models.TextField(blank=True, default='')
    
    # External libraries (for the playground)
    css_libraries = models.JSONField(default=list, blank=True, help_text="ex: ['bootstrap', 'tailwind']")
    js_libraries = models.JSONField(default=list, blank=True, help_text="ex: ['react', 'vue']")
    
    # Viewport settings
    viewport_width = models.PositiveIntegerField(default=1440)
    viewport_height = models.PositiveIntegerField(default=900)
    
    # Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    fork_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'playground_snippets'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['is_public', '-view_count']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    def get_preview_html(self):
        """Generate full HTML for preview."""
        css_libs = ''
        js_libs = ''
        
        if 'bootstrap' in self.css_libraries:
            css_libs += '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">\n'
        if 'tailwind' in self.css_libraries:
            css_libs += '<script src="https://cdn.tailwindcss.com"></script>\n'
        
        if 'react' in self.js_libraries:
            js_libs += '<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>\n'
            js_libs += '<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>\n'
        if 'vue' in self.js_libraries:
            js_libs += '<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>\n'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    {css_libs}
    <style>{self.css_code}</style>
</head>
<body>
{self.html_code}
{js_libs}
<script>{self.js_code}</script>
</body>
</html>"""


class PlaygroundTemplate(models.Model):
    """
    Starter templates for the playground.
    Admin-created to help beginners get started.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='playground_templates/', null=True, blank=True)
    
    html_code = models.TextField(blank=True, default='')
    css_code = models.TextField(blank=True, default='')
    js_code = models.TextField(blank=True, default='')
    
    difficulty = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='beginner'
    )
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'playground_templates'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class CodeChallenge(models.Model):
    """
    Code challenges for users to solve in the playground.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    
    # Starter code
    html_template = models.TextField(blank=True)
    css_template = models.TextField(blank=True)
    js_template = models.TextField(blank=True)
    
    # Solution
    html_solution = models.TextField(blank=True)
    css_solution = models.TextField(blank=True)
    js_solution = models.TextField(blank=True)
    
    # Validation
    tests = models.JSONField(default=list)
    hints = models.JSONField(default=list)
    
    difficulty = models.PositiveIntegerField(default=1, help_text="1-5")
    xp_reward = models.PositiveIntegerField(default=50)
    estimated_minutes = models.PositiveIntegerField(default=30)
    
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'code_challenges'
        ordering = ['order', 'difficulty']
    
    def __str__(self):
        return self.title


class ChallengeSubmission(models.Model):
    """
    User submission for a code challenge.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='challenge_submissions')
    challenge = models.ForeignKey(CodeChallenge, on_delete=models.CASCADE, related_name='submissions')
    
    html_code = models.TextField(blank=True)
    css_code = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    
    passed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=1)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'challenge_submissions'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} {'✅' if self.passed else '❌'}"