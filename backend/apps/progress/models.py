from django.db import models
from django.utils import timezone
import uuid


class UserProgress(models.Model):
    """
    Track individual lesson completion per user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Attempts
    attempts = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    # Score
    score = models.PositiveIntegerField(default=0, help_text="Score on exercises/quizzes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_lesson_progress'
        unique_together = ['user', 'lesson']
        ordering = ['-updated_at']
        verbose_name_plural = 'User progress'
        indexes = [
            models.Index(fields=['user', 'lesson']),
            models.Index(fields=['user', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} {'✅' if self.completed else '⏳'}"
    
    def mark_completed(self):
        """Mark lesson as completed and award XP."""
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            
            # Award XP to user
            self.user.award_xp(self.lesson.xp_reward)
            
            # Create activity log
            from apps.accounts.models import UserActivity
            UserActivity.objects.create(
                user=self.user,
                activity_type='lesson_completed',
                description=f"Completed '{self.lesson.title}'",
                xp_earned=self.lesson.xp_reward,
                metadata={
                    'lesson_id': str(self.lesson.id),
                    'module': self.lesson.module.title,
                    'course': self.lesson.module.course.title,
                }
            )
            
            # Update streak
            self.user.update_streak()


class UserModuleProgress(models.Model):
    """
    Track module-level progress for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='module_progress'
    )
    module = models.ForeignKey(
        'courses.Module',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_module_progress'
        unique_together = ['user', 'module']
        ordering = ['module__order']
    
    def __str__(self):
        return f"{self.user.username} - {self.module.title} {'✅' if self.completed else '🔒'}"
    
    def check_completion(self):
        """Check if all lessons in module are completed."""
        total_lessons = self.module.lessons.count()
        completed_lessons = UserProgress.objects.filter(
            user=self.user,
            lesson__module=self.module,
            completed=True
        ).count()
        
        if total_lessons > 0 and completed_lessons >= total_lessons:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            
            # Award module XP
            self.user.award_xp(self.module.xp_reward)
            
            # Log activity
            from apps.accounts.models import UserActivity
            UserActivity.objects.create(
                user=self.user,
                activity_type='lesson_completed',
                description=f"Completed module '{self.module.title}'",
                xp_earned=self.module.xp_reward,
            )
        
        return self.completed


class UserCourseProgress(models.Model):
    """
    Track course-level progress.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'user_course_progress'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.progress_percent}%)"
    
    def update_progress(self):
        """Calculate and update course progress percentage."""
        total_lessons = self.course.lesson_count
        if total_lessons == 0:
            return 0
        
        completed_lessons = UserProgress.objects.filter(
            user=self.user,
            lesson__module__course=self.course,
            completed=True
        ).count()
        
        self.progress_percent = (completed_lessons / total_lessons) * 100
        
        if self.progress_percent >= 100:
            self.completed = True
            self.completed_at = timezone.now()
            
            # Award course XP
            self.user.award_xp(self.course.xp_reward)
            
            # Log
            from apps.accounts.models import UserActivity
            UserActivity.objects.create(
                user=self.user,
                activity_type='lesson_completed',
                description=f"Completed course '{self.course.title}'! 🎉",
                xp_earned=self.course.xp_reward,
            )
        
        self.save()
        return self.progress_percent


class UserPathProgress(models.Model):
    """
    Track learning path progress.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='path_progress'
    )
    path = models.ForeignKey(
        'courses.Path',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'user_path_progress'
        unique_together = ['user', 'path']
    
    def update_progress(self):
        """Calculate path progress based on course completions."""
        total_courses = self.path.courses.count()
        if total_courses == 0:
            return 0
        
        completed_courses = UserCourseProgress.objects.filter(
            user=self.user,
            course__path=self.path,
            completed=True
        ).count()
        
        self.progress_percent = (completed_courses / total_courses) * 100
        
        if self.progress_percent >= 100:
            self.completed = True
            self.completed_at = timezone.now()
        
        self.save()
        return self.progress_percent


class DailyActivity(models.Model):
    """
    Track daily user activity for streak calculation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='daily_activities'
    )
    date = models.DateField()
    lessons_completed = models.PositiveIntegerField(default=0)
    exercises_completed = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'daily_activities'
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Daily activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @classmethod
    def log_activity(cls, user, lesson=None, exercise=None, xp=0, time_spent=0):
        """Log daily activity - call this whenever user does something."""
        today = timezone.now().date()
        activity, created = cls.objects.get_or_create(
            user=user,
            date=today,
        )
        
        if lesson:
            activity.lessons_completed += 1
        if exercise:
            activity.exercises_completed += 1
        
        activity.xp_earned += xp
        activity.time_spent_seconds += time_spent
        activity.save()
        
        # Update user streak
        user.update_streak()
        
        return activity