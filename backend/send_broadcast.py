import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
import django
django.setup()
from django.core.mail import send_mail
from django.conf import settings
from apps.accounts.models import User

# Get all users
users = User.objects.filter(is_active=True)

subject = input("Subject: ")
message = input("Message: ")

print(f"\nSending to {users.count()} users...")

for user in users:
    try:
        personalized = message.replace('Hi there!', f'Hi {user.username}!')
        send_mail(
            subject=subject,
            message=personalized,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"  ✅ {user.email}")
    except Exception as e:
        print(f"  ❌ {user.email}: {e}")

print("\n✅ Done!")
