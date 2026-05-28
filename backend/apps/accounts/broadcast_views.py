from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from .models import User

@staff_member_required
def broadcast_email(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        recipients = request.POST.getlist('recipients')
        send_to_all = request.POST.get('send_to_all') == 'on'
        
        if not subject or not message:
            messages.error(request, 'Subject and message are required!')
            return redirect('broadcast_email')
        
        # Get users
        if send_to_all:
            users = User.objects.filter(is_active=True)
        elif recipients:
            users = User.objects.filter(id__in=recipients, is_active=True)
        else:
            messages.error(request, 'Select at least one recipient!')
            return redirect('broadcast_email')
        
        # Send emails
        email_list = []
        for user in users:
            email_list.append((
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            ))
        
        try:
            send_mass_mail(email_list, fail_silently=False)
            messages.success(request, f'✅ Email sent to {len(email_list)} users!')
        except Exception as e:
            messages.error(request, f'Failed to send: {e}')
        
        return redirect('broadcast_email')
    
    users = User.objects.filter(is_active=True).order_by('-date_joined')
    return render(request, 'admin/broadcast.html', {'users': users})
