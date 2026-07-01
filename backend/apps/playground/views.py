from django.shortcuts import render

def playground(request):
    return render(request, 'playground.html')

from django.http import JsonResponse
from .ai_mentor import review_code

def ai_review_api(request):
    """API endpoint for AI code review"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        html = data.get('html', '')
        css = data.get('css', '')
        js = data.get('js', '')
        
        result = review_code(html, css, js)
        return JsonResponse(result)
    return JsonResponse({'error': 'POST required'}, status=405)
