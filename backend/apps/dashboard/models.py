from django.db import models
import uuid


class UserStats(models.Model):
    """
    Cached user statistics for dashboard display.
    Updated periodically or on significant actions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='stats'
    )
    
    # Course stats
    total_courses_enrolled = models.PositiveIntegerField(default=0)
    total_courses_completed = models.PositiveIntegerField(default=0)
    total_lessons_completed = models.PositiveIntegerField(default=0)
    total_exercises_completed = models.PositiveIntegerField(default=0)
    
    # Time stats
    total_time_spent_seconds = models.PositiveIntegerField(default=0, help_text="Total learning time")
    average_daily_time_seconds = models.PositiveIntegerField(default=0)
    
    # Streak
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    
    # XP & Level
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    
    # Projects
    total_projects = models.PositiveIntegerField(default=0)
    published_projects = models.PositiveIntegerField(default=0)
    
    # Community
    total_badges = models.PositiveIntegerField(default=0)
    
    # Rankings
    global_rank = models.PositiveIntegerField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_stats'
        verbose_name_plural = 'User stats'
    
    def __str__(self):
        return f"Stats for {self.user.username}"
    
    @property
    def total_time_hours(self):
        return round(self.total_time_spent_seconds / 3600, 1)
    
    @property
    def completion_rate(self):
        if self.total_courses_enrolled == 0:
            return 0
        return round((self.total_courses_completed / self.total_courses_enrolled) * 100)


class LearningGoal(models.Model):
    """
    User's learning goals.
    """
    GOAL_TYPES = [
        ('daily_lessons', 'Daily Lessons'),
        ('weekly_projects', 'Weekly Projects'),
        ('course_completion', 'Course Completion'),
        ('streak', 'Streak Days'),
        ('xp', 'XP Earned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='goals'
    )
    
    goal_type = models.CharField(max_length=30, choices=GOAL_TYPES)
    target = models.PositiveIntegerField()
    current = models.PositiveIntegerField(default=0)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_goals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()}: {self.current}/{self.target}"
    
    @property
    def progress_percent(self):
        if self.target == 0:
            return 100
        return min(100, round((self.current / self.target) * 100))
    
    def update_progress(self, amount=1):
        """Increment progress towards goal."""
        self.current += amount
        if self.current >= self.target:
            self.completed = True
            self.completed_at = timezone.now()
        self.save()