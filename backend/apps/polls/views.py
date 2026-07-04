from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Poll, PollOption, PollVote

def active_polls(request):
    polls = Poll.objects.filter(is_active=True).prefetch_related('options__votes')
    return render(request, 'polls/active.html', {'polls': polls})

@login_required
def vote_poll(request, poll_id):
    option_id = request.POST.get('option_id') or request.GET.get('option_id')
    if option_id:
        option = get_object_or_404(PollOption, id=option_id)
        if PollVote.objects.filter(option__poll=option.poll, user=request.user).exists():
            messages.error(request, 'Already voted!')
        else:
            PollVote.objects.create(option=option, user=request.user)
            messages.success(request, 'Vote recorded!')
    return redirect(request.META.get('HTTP_REFERER', '/polls/'))

@staff_member_required
def create_poll(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        options = request.POST.getlist('options')
        if question and len(options) >= 2:
            poll = Poll.objects.create(question=question, created_by=request.user)
            for opt in options:
                if opt.strip():
                    PollOption.objects.create(poll=poll, text=opt.strip())
            messages.success(request, 'Poll created!')
            return redirect('active_polls')
    return render(request, 'polls/create.html')

def latest_poll_api(request):
    poll = Poll.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-created_at').first()
    if poll:
        options_data = []
        for opt in poll.options.all():
            options_data.append({
                'id': str(opt.id), 'text': opt.text,
                'vote_count': opt.vote_count, 'percentage': opt.percentage,
            })
        return JsonResponse({'poll': {
            'id': str(poll.id), 'question': poll.question,
            'total_votes': poll.total_votes(), 'options': options_data,
        }})
    return JsonResponse({'poll': None})
