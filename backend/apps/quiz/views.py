from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Quiz, Question, QuizAttempt
from apps.accounts.models import UserActivity

def quiz_list(request):
    quizzes = Quiz.objects.filter(is_published=True)
    return render(request, 'quiz/list.html', {'quizzes': quizzes})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    questions = quiz.questions.all().prefetch_related('choices')
    
    if request.method == 'POST':
        # Grade the quiz
        correct = 0
        total = questions.count()
        
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                choice = question.choices.filter(id=answer_id, is_correct=True).first()
                if choice:
                    correct += 1
        
        score = round((correct / total) * 100) if total > 0 else 0
        passed = score >= quiz.passing_score
        
        # Save attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total,
            correct_answers=correct,
            passed=passed,
            completed_at=timezone.now()
        )
        
        # Award XP if passed
        if passed:
            request.user.award_xp(50)
            UserActivity.objects.create(
                user=request.user,
                activity_type='badge_earned',
                description=f"Passed {quiz.title} quiz ({score}%)",
                xp_earned=50
            )
        
        return render(request, 'quiz/result.html', {
            'quiz': quiz,
            'attempt': attempt,
            'correct': correct,
            'total': total,
            'score': score,
            'passed': passed,
        })
    
    return render(request, 'quiz/take.html', {
        'quiz': quiz,
        'questions': questions,
    })

def quiz_results(request):
    if request.user.is_authenticated:
        attempts = QuizAttempt.objects.filter(user=request.user).order_by('-completed_at')[:20]
    else:
        attempts = []
    return render(request, 'quiz/results.html', {'attempts': attempts})
