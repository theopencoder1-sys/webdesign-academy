from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def contact_page(request):
    return render(request, 'contact.html')

def contact_send(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', 'general')
        message = request.POST.get('message', '')
        
        full_message = f'''
New Contact Form Submission
============================
From: {name}
Email: {email}
Subject: {subject}

Message:
{message}
'''
        
        try:
            send_mail(
                subject=f'WebDesign Academy Contact: {subject} - from {name}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['theopencoder1@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Message sent successfully! We will get back to you within 24 hours. ✅')
        except Exception as e:
            messages.error(request, 'Could not send message. Please try again.')
        
        return redirect('contact')
    
    return redirect('contact')
