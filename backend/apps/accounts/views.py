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
            messages.error(request, 'Disposable emails not allowed.')
            return render(request, 'auth/signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/signup.html')
        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = True
        user.verification_token = str(uuid.uuid4())
        user.save()
        verify_link = request.build_absolute_uri(reverse('verify_email', kwargs={'token': user.verification_token}))
        try:
            send_mail('Verify Email', f'Click: {verify_link}', settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        except: pass
        login(request, user)
        messages.success(request, 'Account created! Welcome!')
        return redirect('dashboard')
    return render(request, 'auth/signup.html')

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.email_verified = True
        user.verification_token = None
        user.email_verified_at = timezone.now()
        user.save()
        messages.success(request, 'Email verified!')
        return redirect('dashboard')
    except User.DoesNotExist:
        messages.error(request, 'Invalid link.')
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
                send_mail('Password Reset', f'Click: {reset_link}', settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, 'Reset link sent!')
            except:
                messages.success(request, f'Link: {reset_link}')
            return redirect('login')
        except User.DoesNotExist:
            messages.success(request, 'If email exists, link sent.')
            return redirect('login')
    return render(request, 'auth/forgot_password.html')

def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        messages.error(request, 'Invalid link.')
        return redirect('forgot_password')
    if timezone.now() - user.reset_token_created > timedelta(hours=1):
        messages.error(request, 'Expired.')
        return redirect('forgot_password')
    if request.method == 'POST':
        p1 = request.POST.get('password')
        p2 = request.POST.get('confirm_password')
        if p1 != p2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/reset_password.html', {'token': token})
        if len(p1) < 8:
            messages.error(request, 'Min 8 chars!')
            return render(request, 'auth/reset_password.html', {'token': token})
        user.set_password(p1)
        user.reset_token = None
        user.save()
        messages.success(request, 'Done! Login.')
        return redirect('login')
    return render(request, 'auth/reset_password.html', {'token': token})

def goodbye(request):
    return render(request, 'auth/goodbye.html')
