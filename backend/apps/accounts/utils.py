import re
import requests

def is_valid_email(email):
    """Basic email format validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_disposable_email(email):
    """Check if email is from disposable/temporary email service"""
    domain = email.split('@')[1].lower()
    
    disposable_domains = [
        'mailinator.com', 'guerrillamail.com', 'tempmail.com', '10minutemail.com',
        'yopmail.com', 'throwaway.email', 'sharklasers.com', 'trashmail.com',
        'temp-mail.org', 'fakeinbox.com', 'guerrillamail.org', 'tempmail.org',
        'dispostable.com', 'maildrop.cc', 'harakirimail.com', 'getnada.com',
        'spam4.me', 'wegwerfmail.de', 'mailnesia.com', 'tempr.email',
        'tempemail.co', 'mintemail.com', 'mailcatch.com', 'emailondeck.com',
    ]
    
    return domain in disposable_domains

def is_valid_mx(email):
    """Check if email domain has valid MX records (basic check)"""
    domain = email.split('@')[1]
    # Simple check - in production use DNS lookup
    invalid_domains = ['example.com', 'test.com', 'email.com', 'mail.com', 'nomail.com']
    return domain not in invalid_domains
