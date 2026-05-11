from django.shortcuts import render
from django.http import JsonResponse
import random

def chatbot_page(request):
    return render(request, 'chatbot/chat.html')

def chatbot_response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip().lower()
        if not message:
            return JsonResponse({'response': 'Please type a message!'})
        response = get_bot_response(message)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'POST required'}, status=400)

def get_bot_response(message):
    msg = message.lower()
    
    # Greetings
    if any(word in msg for word in ['hello', 'hi', 'hey', 'yo', 'sup']):
        return "Hey there! I am the WebDesign Academy assistant. Ask me anything about HTML, CSS, JavaScript, or our courses!"
    
    if any(word in msg for word in ['how are you']):
        return "I am great! Ready to help you learn web design!"
    
    if any(word in msg for word in ['thank', 'thanks']):
        return "You are welcome! Happy coding!"
    
    if any(word in msg for word in ['bye', 'goodbye']):
        return "Goodbye! Keep coding!"
    
    # Platform
    if 'course' in msg or 'courses' in msg:
        return "We offer FREE courses: HTML5 (14 sections), CSS Mastery (12 sections), JavaScript Essentials (10 sections). PRO courses: Tailwind CSS, Full-Stack, UI/UX, React, Python, Cybersecurity. Upgrade from Ksh 500/month!"
    
    if 'pro' in msg or 'premium' in msg or 'upgrade' in msg:
        return "PRO Membership: Monthly Ksh 500 or Yearly Ksh 5,700 (save Ksh 1,300!). Unlocks 6 PRO courses, certificates, code reviews. Pay with M-Pesa!"
    
    if 'price' in msg or 'pricing' in msg or 'cost' in msg:
        return "Pricing: Free (HTML, CSS, JS) | Pro Monthly: Ksh 500 | Pro Yearly: Ksh 5,700. Pay with M-Pesa!"
    
    if 'mpesa' in msg or 'pay' in msg or 'payment' in msg:
        return "We accept M-Pesa payments! Go to the Pricing page, choose a plan, and pay with STK Push. Safe and instant!"
    
    # HTML
    if 'html' in msg:
        if 'tag' in msg:
            return "HTML tags are keywords in angle brackets like <tagname>. Most come in pairs: opening <p> and closing </p>. Some are self-closing like <br> and <img>."
        return "HTML (HyperText Markup Language) structures webpages using tags like h1, p, img, etc. It is the foundation of every website!"
    
    # CSS
    if 'css' in msg:
        if 'flexbox' in msg or 'flex' in msg:
            return "Flexbox: display: flex; justify-content: center; align-items: center; gap: 20px; Perfect for 1D layouts!"
        if 'grid' in msg:
            return "CSS Grid: display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; Perfect for 2D layouts!"
        if 'color' in msg or 'background' in msg:
            return "CSS Colors: named (red, blue), hex (#FF0000), RGB (rgb(255,0,0)), RGBA (rgba(255,0,0,0.5)). Background: background-color, background-image, linear-gradient()."
        return "CSS styles HTML elements - colors, fonts, layout, responsiveness. Learn Flexbox, Grid, animations in our free CSS course!"
    
    # JavaScript
    if 'javascript' in msg or 'js' in msg:
        if 'function' in msg:
            return "JavaScript functions: function greet(name) { return 'Hello ' + name; } or arrow: const greet = (name) => 'Hello ' + name;"
        if 'variable' in msg:
            return "Variables: let name = 'Brian'; (changeable) const PI = 3.14; (constant). Never use var!"
        if 'dom' in msg:
            return "DOM: document.querySelector('h1') to select, .textContent to change text, .style.color to change style, .addEventListener('click', fn) for events."
        return "JavaScript adds interactivity to websites. Learn in our free JS course!"
    
    # Python
    if 'python' in msg:
        return "Python is a versatile programming language. Used for web dev (Django), data science, AI, automation. We have a PRO Python course!"
    
    if 'django' in msg:
        return "Django is a Python web framework for building websites quickly. Handles databases, auth, APIs. Covered in PRO Full-Stack course!"
    
    # Tailwind
    if 'tailwind' in msg:
        return "Tailwind CSS is utility-first. Use classes like bg-blue-500, text-white, px-6 directly in HTML. Super fast development! PRO course available."
    
    # React
    if 'react' in msg:
        return "React.js is a JavaScript library for building user interfaces. Uses components, hooks, virtual DOM. Created by Facebook."
    
    # Full-Stack
    if 'full stack' in msg or 'fullstack' in msg or 'backend' in msg:
        return "Full-Stack means frontend (HTML, CSS, JS) + backend (Python/Django, databases). PRO Full-Stack course available!"
    
    # Git
    if 'git' in msg or 'github' in msg:
        return "Git tracks code changes. GitHub stores code online. Commands: git init, git add ., git commit -m 'msg', git push."
    
    # API
    if 'api' in msg:
        return "API allows software to communicate. Example: M-Pesa Daraja API processes payments on our site! REST uses GET, POST, PUT, DELETE."
    
    # Database
    if 'database' in msg or 'sql' in msg:
        return "Databases store data: SQLite (simple), PostgreSQL (powerful), MySQL (popular). SQL: SELECT * FROM users WHERE..."
    
    # Deploy
    if 'deploy' in msg or 'host' in msg or 'live' in msg:
        return "Deploy options: GitHub Pages (free static), PythonAnywhere (free Django), Railway/Render (modern), Netlify/Vercel (frontend)."
    
    # Career
    if 'job' in msg or 'career' in msg or 'salary' in msg:
        return "Web Dev Careers: Junior Frontend Ksh 30K-80K, Full-Stack Ksh 80K-200K, Freelancing Ksh 5K-50K per project. Build a strong portfolio!"
    
    # Tools
    if 'vscode' in msg or 'editor' in msg:
        return "VS Code is the most popular free code editor. Get it from code.visualstudio.com. Extensions: Live Server, Prettier, ESLint."
    
    # Debug
    if 'error' in msg or 'debug' in msg or 'bug' in msg:
        return "Debugging tips: Check browser console (F12), read errors, use console.log(), validate HTML at validator.w3.org, search on Google."
    
    # Motivation
    if 'stuck' in msg or 'hard' in msg or 'motivation' in msg:
        return "Do not give up! Break problems small, practice daily, build projects, join our community. Every expert was once a beginner!"
    
    # Forms
    if 'form' in msg:
        return "HTML Forms: <form> container, <input type='text'> for text, <input type='email'> for email, <textarea> for multiline, <button> to submit."
    
    # Animation
    if 'animation' in msg or 'animate' in msg:
        return "CSS Animations: transition: all 0.3s ease; @keyframes slideIn { from{...} to{...} } transform: scale(1.1) rotate(45deg)."
    
    # Responsive
    if 'responsive' in msg or 'mobile' in msg:
        return "Responsive Design: @media queries, Flexbox/Grid, relative units (%, rem, vh, vw), mobile-first approach. Covered in CSS course!"
    
    # Kenya
    if 'kenya' in msg or 'nairobi' in msg:
        return "Kenya is Silicon Savannah! Nairobi is a growing tech hub. M-Pesa revolutionized mobile payments. Great demand for developers here!"
    
    # Certificate
    if 'certificate' in msg:
        return "Certificates available when you complete a PRO course! Includes your name, course title, date, and verification ID. Great for LinkedIn!"
    
    # Playground
    if 'playground' in msg:
        return "Our Live Playground lets you write HTML, CSS, JS in your browser with instant preview! Features tabs, download, auto-refresh."
    
    # Semantic
    if 'semantic' in msg:
        return "Semantic HTML: header, nav, main, article, section, aside, footer. Better for SEO, accessibility, and readability!"
    
    # Learning path
    if 'learn' in msg or 'start' in msg or 'beginner' in msg:
        return "Start with: 1) HTML (structure), 2) CSS (style), 3) JavaScript (interactivity). All FREE on our platform!"
    
    # Projects
    if 'project' in msg or 'build' in msg:
        return "Practice projects: Portfolio website, M-Pesa calculator, Restaurant menu, Login form, Landing page. Submit on our Projects page!"
    
    # Resources
    if 'resource' in msg or 'book' in msg or 'tutorial' in msg:
        return "Resources: Our courses, MDN Web Docs, freeCodeCamp, YouTube (Traversy Media, Kevin Powell), Frontend Mentor, CodePen."
    
    # Default
    responses = [
        "Interesting! Check our courses for detailed lessons on that topic.",
        "Great question! Try our Playground to practice.",
        "Our community forum might have answers. Visit the Community page!",
        "The best way to learn is by doing. Start with our free HTML course!",
        "Coding is all about practice! Start with HTML, then CSS, then JavaScript.",
    ]
    
    return random.choice(responses)
