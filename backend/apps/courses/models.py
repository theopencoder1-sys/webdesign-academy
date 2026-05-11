from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Technology(models.Model):
    """
    Technologies/tags for courses (HTML, CSS, JS, React, etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or path")
    color = models.CharField(max_length=7, default="#6366f1", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'technologies'
        ordering = ['order', 'name']
        verbose_name_plural = 'Technologies'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Path(models.Model):
    """
    Learning paths that group related courses.
    Example: "Frontend Developer Path", "Full-Stack Path"
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    long_description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='paths/', null=True, blank=True)
    
    # Meta
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    estimated_hours = models.PositiveIntegerField(default=0)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    technologies = models.ManyToManyField(Technology, blank=True)
    
    # Access
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Extras
    career_title = models.CharField(max_length=200, blank=True, help_text="ex: Junior Frontend Developer")
    avg_salary = models.CharField(max_length=50, blank=True, help_text="ex: $65,000 - $95,000")
    
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['order', 'title']
        verbose_name = 'Learning Path'
        verbose_name_plural = 'Learning Paths'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def course_count(self):
        return self.courses.count()
    
    @property
    def total_lessons(self):
        return sum(course.lesson_count for course in self.courses.all())


class Course(models.Model):
    """
    Individual course within a path.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    
    # Relations
    path = models.ForeignKey(
        Path, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='courses'
    )
    technologies = models.ManyToManyField(Technology, blank=True)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)
    video_preview = models.URLField(blank=True)
    
    # Meta
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_hours = models.PositiveIntegerField(default=1)
    xp_reward = models.PositiveIntegerField(default=100, help_text="XP for completing the course")
    
    # Access
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Order
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['order', 'title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def module_count(self):
        return self.modules.count()
    
    @property
    def lesson_count(self):
        return sum(module.lessons.count() for module in self.modules.all())
    
    @property
    def first_module(self):
        return self.modules.order_by('order').first()
    
    @property
    def rating_avg(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def student_count(self):
        return self.enrollments.count()


class Module(models.Model):
    """
    Module within a course. Contains multiple lessons.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Order within course
    order = models.PositiveIntegerField(default=0)
    
    # Access (can override course)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    # Meta
    xp_reward = models.PositiveIntegerField(default=30)
    estimated_hours = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.course.title} → {self.title}"
    
    @property
    def lesson_count(self):
        return self.lessons.count()


class Lesson(models.Model):
    """
    Individual lesson within a module.
    """
    LESSON_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('interactive', 'Interactive'),
        ('challenge', 'Challenge'),
        ('quiz', 'Quiz'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    
    # Content
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='article')
    content = models.TextField(help_text="Markdown or HTML content")
    summary = models.TextField(blank=True, help_text="TL;DR for the lesson")
    
    # Video (if applicable)
    video_url = models.URLField(blank=True)
    video_duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    
    # Order
    order = models.PositiveIntegerField(default=0)
    
    # Access (can override module)
    is_premium = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    # Gamification
    xp_reward = models.PositiveIntegerField(default=10)
    estimated_minutes = models.PositiveIntegerField(default=10)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['order', 'title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.module.course.title} → {self.module.title} → {self.title}"
    
    @property
    def next_lesson(self):
        """Get the next lesson in the module."""
        return Lesson.objects.filter(
            module=self.module,
            order__gt=self.order
        ).order_by('order').first()
    
    @property
    def prev_lesson(self):
        """Get the previous lesson in the module."""
        return Lesson.objects.filter(
            module=self.module,
            order__lt=self.order
        ).order_by('-order').first()


class Exercise(models.Model):
    """
    Coding exercise attached to a lesson.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    
    # Code templates
    initial_code = models.TextField(help_text="Code shown to user when they start")
    solution = models.TextField(help_text="Correct solution")
    
    # Hints (shown progressively)
    hints = models.JSONField(default=list, help_text="List of hints from easy to detailed")
    
    # Validation
    tests = models.JSONField(default=list, help_text="Test cases to validate solution")
    
    # Meta
    xp_reward = models.PositiveIntegerField(default=20)
    difficulty = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercises'
        ordering = ['order']
    
    def __str__(self):
        return f"Exercise: {self.title}"


class CourseReview(models.Model):
    """
    Student review/rating for a course.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_reviews'
        unique_together = ['course', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}★)"


class Enrollment(models.Model):
    """
    Track which courses/paths a user is enrolled in.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    path = models.ForeignKey(Path, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = [['user', 'course'], ['user', 'path']]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.course:
            return f"{self.user.username} enrolled in {self.course.title}"
        return f"{self.user.username} enrolled in {self.path.title}"
    
    def update_progress(self, completed_lessons, total_lessons):
        """Update enrollment progress percentage."""
        if total_lessons > 0:
            self.progress_percent = (completed_lessons / total_lessons) * 100
            
            if self.progress_percent >= 100:
                self.completed = True
                self.completed_at = timezone.now()
            
            self.save()