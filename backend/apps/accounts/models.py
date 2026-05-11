from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class User(AbstractUser):
    """
    Custom User model.
    Extends Django's AbstractUser with extra fields for our learning platform.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        unique=True,
        db_index=True
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell us about yourself"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    
    # Gamification
    xp = models.PositiveIntegerField(
        default=0,
        help_text="Total experience points earned"
    )
    level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    streak = models.PositiveIntegerField(
        default=0,
        help_text="Consecutive days active"
    )
    longest_streak = models.PositiveIntegerField(
        default=0
    )
    last_active = models.DateField(
        null=True,
        blank=True
    )
    
    # Profile
    title = models.CharField(
        max_length=100,
        blank=True,
        default="Beginner Coder",
        help_text="Display title like 'Full-Stack Developer'"
    )
    website = models.URLField(
        blank=True
    )
    twitter_handle = models.CharField(
        max_length=50,
        blank=True
    )
    github_username = models.CharField(
        max_length=50,
        blank=True
    )
    
    # Preferences
    email_notifications = models.BooleanField(
        default=True
    )
    dark_mode = models.BooleanField(
        default=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Auth
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Password reset fields
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_created = models.DateTimeField(null=True, blank=True)
    
    # Email verification
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['-xp']),  # Leaderboard queries
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()
    
    def update_streak(self):
        """Update streak when user is active."""
        today = timezone.now().date()
        
        if self.last_active is None:
            self.streak = 1
        elif self.last_active == today:
            pass  # Already logged today
        elif self.last_active == today - timezone.timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1  # Broke streak
        
        self.last_active = today
        
        if self.streak > self.longest_streak:
            self.longest_streak = self.streak
        
        self.save(update_fields=['streak', 'longest_streak', 'last_active'])
    
    def calculate_level(self):
        """Calculate level based on XP. Each level requires more XP."""
        # Level formula: level = 1 + sqrt(xp / 100)
        import math
        self.level = max(1, 1 + int(math.sqrt(self.xp / 100)))
        self.save(update_fields=['level'])
    
    @property
    def is_premium(self):
        """Check if user has active subscription."""
        try:
            return self.subscription.is_active
        except Exception:
            return False
    
    @property
    def xp_to_next_level(self):
        """XP needed for next level."""
        if self.level < 1:
            return 100
        return ((self.level) ** 2) * 100 - self.xp
    
    @property
    def level_progress_percent(self):
        """Progress percentage to next level."""
        current_level_xp = ((self.level - 1) ** 2) * 100 if self.level > 1 else 0
        next_level_xp = (self.level ** 2) * 100
        xp_in_current_level = self.xp - current_level_xp
        xp_needed_for_next = next_level_xp - current_level_xp
        
        if xp_needed_for_next <= 0:
            return 100
        
        return min(100, int((xp_in_current_level / xp_needed_for_next) * 100))
    
    def award_xp(self, amount):
        """Award XP and recalculate level."""
        self.xp += amount
        self.calculate_level()
        return self.level


class UserActivity(models.Model):
    """Track individual user actions for analytics."""
    
    ACTIVITY_TYPES = [
        ('lesson_started', 'Lesson Started'),
        ('lesson_completed', 'Lesson Completed'),
        ('exercise_attempted', 'Exercise Attempted'),
        ('exercise_solved', 'Exercise Solved'),
        ('project_submitted', 'Project Submitted'),
        ('streak_achieved', 'Streak Achieved'),
        ('level_up', 'Leveled Up'),
        ('badge_earned', 'Badge Earned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    xp_earned = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True, help_text="Extra activity data")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class Badge(models.Model):
    """Achievement badges users can earn."""
    
    BADGE_CATEGORIES = [
        ('streak', 'Streak'),
        ('courses', 'Courses'),
        ('projects', 'Projects'),
        ('community', 'Community'),
        ('special', 'Special'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    category = models.CharField(max_length=20, choices=BADGE_CATEGORIES)
    xp_reward = models.PositiveIntegerField(default=0)
    criteria = models.JSONField(help_text="Conditions to earn this badge")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Badges earned by users."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_badges'
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"