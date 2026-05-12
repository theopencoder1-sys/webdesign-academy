from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivity, Badge, UserBadge
from django.urls import reverse
from django.http import HttpResponseRedirect

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'email_verified', 'is_active', 'is_premium', 'xp', 'date_joined']
    list_filter = ['email_verified', 'is_active', 'is_premium', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    
    actions = ['verify_users', 'delete_with_goodbye']
    
    def verify_users(self, request, queryset):
        for user in queryset:
            user.email_verified = True
            user.is_active = True
            user.save()
        self.message_user(request, f'Verified {queryset.count()} users')
    verify_users.short_description = "✅ Verify selected users"
    
    def delete_with_goodbye(self, request, queryset):
        for user in queryset:
            user.delete()
        return HttpResponseRedirect(reverse('goodbye'))
    delete_with_goodbye.short_description = "🗑️ Delete users & show goodbye"

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'xp_earned', 'created_at']
    list_filter = ['activity_type', 'created_at']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'xp_reward']

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
