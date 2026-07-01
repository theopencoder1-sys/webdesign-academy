from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import json

@csrf_exempt
def send_broadcast_api(request):
    """API endpoint to send broadcast emails - run locally"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        subject = data.get('subject', '')
        message = data.get('message', '')
        user_ids = data.get('user_ids', [])
        send_to_all = data.get('send_to_all', False)
        
        if not subject or not message:
            return JsonResponse({'error': 'Subject and message required'}, status=400)
        
        if send_to_all:
            users = User.objects.filter(is_active=True)
        elif user_ids:
            users = User.objects.filter(id__in=user_ids, is_active=True)
        else:
            return JsonResponse({'error': 'No recipients'}, status=400)
        
        sent = 0
        failed = []
        
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
                sent += 1
            except Exception as e:
                failed.append({'email': user.email, 'error': str(e)})
        
        return JsonResponse({
            'success': True,
            'sent': sent,
            'failed': failed,
            'total': users.count()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
