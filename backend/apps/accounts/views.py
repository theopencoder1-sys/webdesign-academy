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
        
        # Validate email format
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address!')
            return render(request, 'auth/signup.html')
        
        # Check disposable email
        if is_disposable_email(email):
            messages.error(request, 'Disposable email addresses are not allowed. Please use a real email!')
            return render(request, 'auth/signup.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered. Please login instead.')
            return render(request, 'auth/signup.html')
        
        # Create user (inactive until email verified)
        user = User.objects.create_user(email=email, username=username, password=password)
        user.is_active = False
        user.verification_token = str(uuid.uuid4())
        user.save()
        
        # Build verification link
        verify_link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': user.verification_token})
        )
        
        # Send verification email
        try:
            send_mail(
                subject='Verify Your Email - WebDesign Academy',
                message=f'''Hi {username},

Welcome to WebDesign Academy! 

Please verify your email address by clicking the link below:

{verify_link}

This link expires in 24 hours.

If you did not create this account, please ignore this email.

- WebDesign Academy Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Account created! Check your email to verify your account.')
        except Exception as e:
            print(f"Email error: {e}")
            # Dev fallback
            messages.success(request, f'Account created! Verify link: {verify_link}')
        
        return redirect('login')
    
    return render(request, 'auth/signup.html')

def verify_email(request, token):
    """Verify email with token"""
    try:
        user = User.objects.get(verification_token=token)
        
        if user.email_verified:
            messages.info(request, 'Email already verified. Please login.')
            return redirect('login')
        
        # Verify the email
        user.email_verified = True
        user.is_active = True
        user.email_verified_at = timezone.now()
        user.verification_token = None
        user.save()
        
        # Send welcome email after verification
        try:
            send_mail(
                subject='Welcome to WebDesign Academy!',
                message=f'''Hi {user.username},

Your email has been verified! Welcome to WebDesign Academy!

Start learning web design today:
- Free HTML, CSS & JavaScript courses
- Live code playground
- Portfolio projects
- Community forum

Get started: http://127.0.0.1:8000/courses/

Happy coding!
- WebDesign Academy Team''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass
        
        # Auto-login
        login(request, user)
        messages.success(request, 'Email verified! Welcome to WebDesign Academy!')
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
            if not user.email_verified:
                messages.error(request, 'Please verify your email first. Check your inbox!')
                return render(request, 'auth/login.html')
            
            login(request, user)
            user.update_streak()
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        
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
    """Resend verification email"""
    if request.user.email_verified:
        messages.info(request, 'Email already verified!')
        return redirect('dashboard')
    
    if not request.user.verification_token:
        request.user.verification_token = str(uuid.uuid4())
        request.user.save()
    
    verify_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': request.user.verification_token})
    )
    
    try:
        send_mail(
            subject='Verify Your Email - WebDesign Academy',
            message=f'Click here to verify: {verify_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        messages.success(request, 'Verification email resent! Check your inbox.')
    except:
        messages.success(request, f'Dev mode - Verify link: {verify_link}')
    
    return redirect('dashboard')

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
                send_mail(
                    subject='Password Reset - WebDesign Academy',
                    message=f'''Hi {user.username},

Click below to reset your password:
{reset_link}

This link expires in 1 hour.

- WebDesign Academy Team''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link sent to your email!')
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
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('forgot_password')
    
    if timezone.now() - user.reset_token_created > timedelta(hours=1):
        messages.error(request, 'Reset link has expired.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/reset_password.html', {'token': token})
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'auth/reset_password.html', {'token': token})
        
        user.set_password(password)
        user.reset_token = None
        user.reset_token_created = None
        user.save()
        
        messages.success(request, 'Password reset successfully! Please login.')
        return redirect('login')
    
    return render(request, 'auth/reset_password.html', {'token': token})
