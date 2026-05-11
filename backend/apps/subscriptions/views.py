from django.shortcuts import render
from .models import Plan

def pricing(request):
    plans = Plan.objects.filter(is_active=True).order_by('order')
    return render(request, 'pricing.html', {'plans': plans})
