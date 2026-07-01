import re

def review_code(html, css, js):
    """AI-style code review - gives personalized feedback"""
    feedback = []
    score = 100
    
    # HTML Review
    if html:
        if '<!DOCTYPE html>' not in html:
            feedback.append("⚠️ Missing DOCTYPE declaration. Add <!DOCTYPE html> at the top.")
            score -= 10
        if '<html' not in html:
            feedback.append("⚠️ Missing <html> tag. This is required for every HTML document.")
            score -= 10
        if '<head>' not in html or '<body>' not in html:
            feedback.append("⚠️ Missing <head> or <body> section. Every page needs both.")
            score -= 10
        if '<title>' not in html:
            feedback.append("💡 Add a <title> tag for better SEO and browser tab text.")
            score -= 5
        if 'alt=' not in html and '<img' in html:
            feedback.append("⚠️ Images without alt text. Always add alt for accessibility!")
            score -= 5
        if '<h1>' in html and html.count('<h1>') > 1:
            feedback.append("💡 You have multiple <h1> tags. Use only ONE per page for best SEO.")
            score -= 5
    
    # CSS Review
    if css:
        if 'flex' not in css and 'grid' not in css:
            feedback.append("💡 Try using Flexbox or Grid for layout. It makes responsive design much easier!")
        if 'px' in css and 'rem' not in css and 'em' not in css:
            feedback.append("💡 Consider using rem/em units instead of px for better accessibility.")
        if 'media' not in css:
            feedback.append("💡 Add @media queries to make your design responsive on mobile devices.")
        if css.count('!important') > 2:
            feedback.append("⚠️ Too many !important declarations. This can cause specificity issues.")
            score -= 5
    
    # JS Review
    if js:
        if 'var ' in js:
            feedback.append("⚠️ Using var instead of let/const. var is outdated - use const (default) or let.")
            score -= 10
        if 'console.log' in js:
            feedback.append("💡 console.log is great for debugging, but remove it in production code.")
        if '==' in js and '===' not in js:
            feedback.append("⚠️ Using == instead of ===. Always use strict equality (===) to avoid bugs.")
            score -= 5
        if 'function' in js and '=>' not in js:
            feedback.append("💡 Try arrow functions for cleaner code: const fn = () => {}")
    
    # General feedback
    if not feedback:
        feedback.append("🎉 Great job! Your code looks clean and well-structured!")
    else:
        feedback.insert(0, f"📊 Code Score: {score}/100")
        
    if score >= 90:
        feedback.append("🌟 Excellent work! You're writing professional-quality code.")
    elif score >= 70:
        feedback.append("👍 Good start! Fix the warnings above to improve your code.")
    else:
        feedback.append("📚 Keep learning! Review the suggestions above and try again.")
    
    return {
        'score': score,
        'feedback': feedback,
        'html_tips': len([f for f in feedback if 'HTML' in f or 'DOCTYPE' in f or 'tag' in f]),
        'css_tips': len([f for f in feedback if 'CSS' in f or 'Flexbox' in f or 'responsive' in f]),
        'js_tips': len([f for f in feedback if 'JS' in f or 'var' in f or 'function' in f]),
    }
