from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from .models import User
import os
from datetime import datetime

@staff_member_required
def broadcast_email(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        send_to_all = request.POST.get('send_to_all') == 'on'
        recipients = request.POST.getlist('recipients')
        
        if not subject or not message:
            messages.error(request, 'Subject and message are required!')
            return redirect('broadcast_email')
        
        if send_to_all:
            users = User.objects.filter(is_active=True)
        elif recipients:
            users = User.objects.filter(id__in=recipients, is_active=True)
        else:
            messages.error(request, 'Select at least one recipient!')
            return redirect('broadcast_email')
        
        # Save emails to a file on the server
        filepath = '/home/Dancoder1/broadcast_emails.txt'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        with open(filepath, 'w') as f:
            f.write(f'SUBJECT: {subject}\n')
            f.write(f'Sent: {timestamp}\n')
            f.write(f'To: {users.count()} users\n')
            f.write('='*50 + '\n\n')
            
            for i, user in enumerate(users, 1):
                personalized = message.replace('Hi there!', f'Hi {user.username}!')
                f.write(f'{i}. TO: {user.email}\n')
                f.write(f'   SUBJECT: {subject}\n\n')
                f.write(f'   {personalized}\n')
                f.write(f'\n{"-"*40}\n\n')
        
        messages.success(request, f'✅ Saved {users.count()} emails to broadcast_emails.txt!')
        messages.info(request, f'📁 File saved at: {filepath}')
        messages.info(request, '📋 Copy-paste into Gmail to send!')
        
        return redirect('broadcast_email')
    
    users = User.objects.filter(is_active=True).order_by('-date_joined')
    
    # Show preview of saved file
    filepath = '/home/Dancoder1/broadcast_emails.txt'
    saved_preview = ''
    if os.path.exists(filepath):
        with open(filepath) as f:
            saved_preview = f.read()[:3000]
    
    return render(request, 'admin/broadcast.html', {
        'users': users,
        'saved_preview': saved_preview
    })
