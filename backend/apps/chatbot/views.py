from django.shortcuts import render
from django.http import JsonResponse
from .models import ChatKnowledge
import random
import re

def chatbot_page(request):
    return render(request, 'chatbot/chat.html')

def chatbot_response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if not message:
            return JsonResponse({'response': 'Please type a message!'})
        
        response = get_bot_response(message)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'POST required'}, status=400)

def get_bot_response(message):
    msg = message.lower().strip()
    
    # First, check the knowledge base
    knowledge_items = ChatKnowledge.objects.filter(is_active=True).order_by('-priority')
    
    for item in knowledge_items:
        keywords = [k.strip().lower() for k in item.keywords.split(',')]
        # Check if ANY keyword matches
        for keyword in keywords:
            if keyword in msg:
                return item.response
    
    # Fallback to built-in responses if no knowledge base match
    return built_in_response(msg)

def built_in_response(msg):
    # Greetings
    if any(word in msg for word in ['hello', 'hi', 'hey', 'yo', 'sup']):
        return "Hey there! I'm the WebDesign Academy assistant. Ask me anything about HTML, CSS, JavaScript, or our courses!"
    
    if any(word in msg for word in ['how are you']):
        return "I'm great! Ready to help you learn web design!"
    
    if any(word in msg for word in ['thank', 'thanks']):
        return "You're welcome! Happy coding!"
    
    if any(word in msg for word in ['bye', 'goodbye']):
        return "Goodbye! Keep coding!"
    
    # Platform
    if 'course' in msg or 'courses' in msg:
        return "We offer FREE courses: HTML5 (50+ sections), CSS Mastery, JavaScript Essentials. PRO courses: Tailwind, Full-Stack, UI/UX, React, Python, Cybersecurity. Upgrade from Ksh 500/month!"
    
    if 'pro' in msg or 'premium' in msg:
        return "PRO Membership: Monthly Ksh 500 or Yearly Ksh 5,700. Unlocks 6 PRO courses, certificates, code reviews, mentorship. Pay with M-Pesa!"
    
    if 'price' in msg or 'pricing' in msg or 'cost' in msg:
        return "Pricing: Free (HTML, CSS, JS) | Pro Monthly: Ksh 500 | Pro Yearly: Ksh 5,700. Pay with M-Pesa!"
    
    if 'mpesa' in msg or 'pay' in msg or 'payment' in msg:
        return "We accept M-Pesa payments! Go to the Pricing page, choose a plan, and pay with STK Push."
    
    # HTML
    if 'html' in msg:
        if 'tag' in msg:
            return "HTML tags are keywords in angle brackets like <tagname>. Most come in pairs: opening <p> and closing </p>."
        return "HTML (HyperText Markup Language) structures webpages. It's the foundation of every website!"
    
    # CSS
    if 'css' in msg:
        if 'flexbox' in msg:
            return "Flexbox: display: flex; justify-content: center; align-items: center; gap: 20px;"
        if 'grid' in msg:
            return "CSS Grid: display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;"
        return "CSS styles HTML elements - colors, fonts, layout, responsiveness."
    
    # JavaScript
    if 'javascript' in msg or 'js' in msg:
        return "JavaScript adds interactivity to websites. Variables, functions, DOM, events, APIs."
    
    # Python
    if 'python' in msg:
        return "Python is versatile - web dev (Django), data science, AI, automation. PRO course available!"
    
    if 'django' in msg:
        return "Django is a Python web framework. Models, Views, Templates, ORM, Admin panel. Covered in PRO Full-Stack!"
    
    # Tailwind
    if 'tailwind' in msg:
        return "Tailwind CSS is utility-first. Use classes like bg-blue-500, text-white, px-6. PRO course!"
    
    # React
    if 'react' in msg:
        return "React.js is a JavaScript library for UIs. Components, hooks, virtual DOM. Created by Facebook."
    
    # Career
    if 'job' in msg or 'career' in msg or 'salary' in msg:
        return "Web Dev Careers in Kenya: Junior Ksh 30K-80K, Full-Stack Ksh 80K-200K, Freelancing Ksh 5K-50K per project."
    
    # Default
    responses = [
        "Interesting! Check our courses for detailed lessons.",
        "Great question! Try our Playground to practice.",
        "Our community forum might have answers.",
        "Start with our free HTML course!",
        "Practice makes perfect! 💪",
    ]
    return random.choice(responses)
