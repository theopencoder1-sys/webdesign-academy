from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import uuid
import stripe
from django.conf import settings


class Plan(models.Model):
    """
    Subscription plans.
    """
    PLAN_TYPES = [
        ('free', 'Free'),
        ('pro_monthly', 'Pro Monthly'),
        ('pro_yearly', 'Pro Yearly'),
        ('lifetime', 'Lifetime'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    duration_days = models.PositiveIntegerField(
        default=0, 
        help_text="0 for infinite (lifetime/free)"
    )
    
    # Features
    features = models.JSONField(
        default=list,
        help_text="List of feature strings to display"
    )
    
    # Stripe
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text="Stripe Price ID")
    stripe_product_id = models.CharField(max_length=100, blank=True, help_text="Stripe Product ID")
    
    # Meta
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Highlight as recommended plan")
    order = models.PositiveIntegerField(default=0)
    
    # Limits
    max_projects = models.PositiveIntegerField(default=3, help_text="Max portfolio projects")
    max_daily_exercises = models.PositiveIntegerField(default=10, help_text="Max exercises per day")
    access_all_courses = models.BooleanField(default=False)
    access_premium_content = models.BooleanField(default=False)
    certificate_access = models.BooleanField(default=False)
    code_review_access = models.BooleanField(default=False)
    community_access = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'plans'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} (${self.price}/{self.get_plan_type_display()})"
    
    @property
    def is_free(self):
        return self.plan_type == 'free'
    
    @property
    def price_monthly_equivalent(self):
        """Calculate monthly equivalent price for display."""
        if self.plan_type == 'pro_yearly' and self.price > 0:
            return round(self.price / 12, 2)
        return self.price
    
    @property
    def savings_percent(self):
        """Calculate savings for yearly vs monthly."""
        if self.plan_type == 'pro_yearly':
            try:
                monthly = Plan.objects.get(plan_type='pro_monthly')
                if monthly.price > 0:
                    yearly_monthly_equiv = self.price / 12
                    savings = ((monthly.price - yearly_monthly_equiv) / monthly.price) * 100
                    return round(savings)
            except Plan.DoesNotExist:
                pass
        return 0


class Subscription(models.Model):
    """
    User's active subscription.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('trialing', 'Trialing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    # Dates
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Stripe
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Billing
    cancel_at_period_end = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=True)
    
    # Usage tracking
    projects_used_this_month = models.PositiveIntegerField(default=0)
    exercises_done_today = models.PositiveIntegerField(default=0)
    last_exercise_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    def is_valid(self):
        """Check if subscription is currently valid."""
        if not self.is_active or self.plan.is_free:
            return False
        
        if self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.status = 'canceled'
            self.save()
            return False
        
        if self.cancel_at_period_end:
            return True  # Still valid until period ends
        
        return self.status == 'active' or self.status == 'trialing'
    
    def activate_plan(self, plan, stripe_subscription_id=None, stripe_customer_id=None):
        """Activate a new subscription plan."""
        self.plan = plan
        self.status = 'active'
        self.is_active = True
        self.start_date = timezone.now()
        self.cancel_at_period_end = False
        
        if self.stripe_subscription_id:
            self.stripe_subscription_id = stripe_subscription_id
        if stripe_customer_id:
            self.stripe_customer_id = stripe_customer_id
        
        # Set end date based on plan duration
        if plan.duration_days > 0:
            self.end_date = timezone.now() + relativedelta(days=plan.duration_days)
        else:
            self.end_date = None  # Lifetime
        
        self.save()
    
    def cancel(self, at_period_end=True):
        """Cancel subscription."""
        if at_period_end:
            self.cancel_at_period_end = True
            self.save()
            
            # Update Stripe if applicable
            if self.stripe_subscription_id:
                try:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    stripe.Subscription.modify(
                        self.stripe_subscription_id,
                        cancel_at_period_end=True
                    )
                except Exception:
                    pass  # Log this in production
        else:
            self.status = 'canceled'
            self.is_active = False
            self.canceled_at = timezone.now()
            self.save()
    
    def reset_daily_exercise_count(self):
        """Reset daily exercise counter if it's a new day."""
        today = timezone.now().date()
        if self.last_exercise_date != today:
            self.exercises_done_today = 0
            self.last_exercise_date = today
            self.save(update_fields=['exercises_done_today', 'last_exercise_date'])
    
    def can_do_exercise(self):
        """Check if user can do another exercise today based on their plan."""
        self.reset_daily_exercise_count()
        return self.exercises_done_today < self.plan.max_daily_exercises
    
    def can_create_project(self):
        """Check if user can create more projects."""
        return self.projects_used_this_month < self.plan.max_projects
    
    @property
    def days_remaining(self):
        """Days remaining in subscription."""
        if not self.end_date:
            return None  # Lifetime
        delta = self.end_date - timezone.now()
        return max(0, delta.days)


class PaymentHistory(models.Model):
    """
    Record of all payments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, default='completed')
    
    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    receipt_url = models.URLField(blank=True)
    
    # Meta
    description = models.CharField(max_length=255, blank=True)
    billing_reason = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']
        verbose_name_plural = 'Payment histories'
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"