from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import User
from .utils import is_valid_email, is_disposable_email
import uuid
from datetime import timedelta

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address!')
            return render(request, 'auth/signup.html')
        
        if is_disposable_email(email):
            messages.error(request, 'Disposable emails not allowed. Use a real email!')
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login.')
            return render(request, 'auth/signup.html')
        
        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = True
        user.verification_token = str(uuid.uuid4())
        user.save()
        
        verify_link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': user.verification_token})
        )
        
        try:
            send_mail(
                subject='Verify Your Email - WebDesign Academy',
                message=f'Hi {username},\n\nWelcome to WebDesign Academy! 🇰🇪\n\nClick to verify: {verify_link}\n\n- WebDesign Academy Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except:
            pass
        
        gmail_url = f'https://mail.google.com/mail/u/0/#search/{email}'
        
        return render(request, 'auth/check_email.html', {
            'email': email,
            'gmail_url': gmail_url,
            'verify_link': verify_link
        })
    
    return render(request, 'auth/signup.html')

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.email_verified = True
        user.verification_token = None
        user.email_verified_at = timezone.now()
        user.save()
        login(request, user)
        messages.success(request, 'Email verified! Welcome! 🎉')
        return redirect('dashboard')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('signup')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            user.update_streak()
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'auth/profile.html')

@login_required
def resend_verification(request):
    if request.user.email_verified:
        return redirect('dashboard')
    if not request.user.verification_token:
        request.user.verification_token = str(uuid.uuid4())
        request.user.save()
    verify_link = request.build_absolute_uri(reverse('verify_email', kwargs={'token': request.user.verification_token}))
    try:
        send_mail('Verify Email', f'Click: {verify_link}', settings.DEFAULT_FROM_EMAIL, [request.user.email])
    except:
        pass
    return render(request, 'auth/check_email.html', {'email': request.user.email, 'gmail_url': f'https://mail.google.com/mail/u/0/#search/{request.user.email}', 'verify_link': verify_link})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            user.reset_token = str(uuid.uuid4())
            user.reset_token_created = timezone.now()
            user.save()
            reset_link = request.build_absolute_uri(f'/auth/reset-password/{user.reset_token}/')
            try:
                send_mail('Password Reset', f'Click to reset: {reset_link}', settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, 'Reset link sent to your email!')
            except:
                messages.success(request, f'Reset link: {reset_link}')
            return redirect('login')
        except User.DoesNotExist:
            messages.success(request, 'If that email exists, a reset link has been sent.')
            return redirect('login')
    return render(request, 'auth/forgot_password.html')

def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired link.')
        return redirect('forgot_password')
    if timezone.now() - user.reset_token_created > timedelta(hours=1):
        messages.error(request, 'Link expired.')
        return redirect('forgot_password')
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/reset_password.html', {'token': token})
        if len(password) < 8:
            messages.error(request, 'Min 8 characters!')
            return render(request, 'auth/reset_password.html', {'token': token})
        user.set_password(password)
        user.reset_token = None
        user.save()
        messages.success(request, 'Password reset! Please login.')
        return redirect('login')
    return render(request, 'auth/reset_password.html', {'token': token})


def goodbye(request):
    return render(request, 'auth/goodbye.html')
