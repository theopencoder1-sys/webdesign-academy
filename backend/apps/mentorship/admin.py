from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import MentorshipSession, Availability, CodeReview

@admin.register(MentorshipSession)
class MentorshipSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'session_date', 'status', 'created_at']
    list_filter = ['status', 'session_date']
    search_fields = ['user__email', 'topic']
    actions = ['approve_sessions', 'reject_sessions']
    
    def approve_sessions(self, request, queryset):
        for session in queryset:
            session.status = 'approved'
            session.meet_link = 'https://meet.google.com/abc-defg-hij'
            session.save()
            try:
                send_mail(
                    subject='✅ Mentorship Session Approved!',
                    message=f'''Hi {session.user.username},

Your mentorship session has been APPROVED!

Topic: {session.topic}
Date: {session.session_date.strftime('%B %d, %Y at %I:%M %p')}
Meet Link: {session.meet_link}

See you soon!
- Dancan Njoro''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[session.user.email],
                    fail_silently=True,
                )
            except:
                pass
        self.message_user(request, f'Approved {queryset.count()} sessions')
    approve_sessions.short_description = "✅ Approve & send confirmation email"
    
    def reject_sessions(self, request, queryset):
        for session in queryset:
            session.status = 'rejected'
            session.save()
            try:
                send_mail(
                    subject='Mentorship Session Update',
                    message=f'Hi {session.user.username},\n\nUnfortunately, the session "{session.topic}" cannot be accommodated. Please book another slot.\n\n- Dancan',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[session.user.email],
                    fail_silently=True,
                )
            except:
                pass
        self.message_user(request, f'Rejected {queryset.count()} sessions')
    reject_sessions.short_description = "❌ Reject & notify user"

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['get_day_display', 'start_time', 'end_time', 'max_sessions', 'is_active']

@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'created_at']
