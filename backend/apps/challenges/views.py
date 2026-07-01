from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import DailyChallenge, ChallengeSubmission
from apps.playground.ai_mentor import review_code
from apps.accounts.models import UserActivity
import json

def challenge_list(request):
    today = timezone.now().date()
    challenges = DailyChallenge.objects.filter(is_active=True).order_by('-date')[:30]
    today_challenge = DailyChallenge.objects.filter(date=today, is_active=True).first()
    
    user_submissions = {}
    if request.user.is_authenticated:
        subs = ChallengeSubmission.objects.filter(user=request.user)
        user_submissions = {str(s.challenge_id): s for s in subs}
    
    return render(request, 'challenges/list.html', {
        'challenges': challenges,
        'today_challenge': today_challenge,
        'user_submissions': user_submissions,
    })

@login_required
def submit_challenge(request, challenge_id):
    if request.method == 'POST':
        challenge = get_object_or_404(DailyChallenge, id=challenge_id)
        code = request.POST.get('code', '')
        
        # AI Review
        result = review_code(code, '', '')
        score = result['score']
        completed = score >= 70
        
        submission, created = ChallengeSubmission.objects.update_or_create(
            user=request.user,
            challenge=challenge,
            defaults={
                'code': code,
                'score': score,
                'completed': completed,
            }
        )
        
        if completed:
            request.user.award_xp(challenge.points)
            UserActivity.objects.create(
                user=request.user,
                activity_type='lesson_completed',
                description=f"Completed daily challenge: {challenge.title}",
                xp_earned=challenge.points,
            )
        
        return JsonResponse({
            'success': True,
            'score': score,
            'completed': completed,
            'feedback': result['feedback'],
        })
    
    return JsonResponse({'error': 'POST required'}, status=405)
