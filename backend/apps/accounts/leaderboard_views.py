from django.shortcuts import render
from .models import User

def leaderboard(request):
    top_learners = User.objects.filter(is_active=True).order_by('-xp')[:50]
    return render(request, 'leaderboard.html', {'top_learners': top_learners})
