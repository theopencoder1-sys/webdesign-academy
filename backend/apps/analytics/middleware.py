import uuid
from .models import PageView

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip admin, static, and API requests
        path = request.path
        if not any(path.startswith(p) for p in ['/admin/', '/static/', '/media/', '/mpesa/']):
            try:
                # Determine device type
                user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
                # Detect browser
                if 'edg/' in user_agent:
                    browser = 'Edge'
                elif 'chrome' in user_agent and 'brave' not in user_agent:
                    browser = 'Chrome'
                elif 'firefox' in user_agent:
                    browser = 'Firefox'
                elif 'safari' in user_agent and 'chrome' not in user_agent:
                    browser = 'Safari'
                elif 'opera' in user_agent or 'opr/' in user_agent:
                    browser = 'Opera'
                elif 'brave' in user_agent:
                    browser = 'Brave'
                else:
                    browser = 'Other'
                # Detect device
                if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                    device = browser + ' 📱'
                elif 'tablet' in user_agent or 'ipad' in user_agent:
                    device = browser + ' 📋'
                else:
                    device = browser + ' 💻'
                
                # Get or create session ID
                session_id = request.session.get('analytics_session_id')
                if not session_id:
                    session_id = str(uuid.uuid4())[:8]
                    request.session['analytics_session_id'] = session_id
                
                PageView.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    page_url=path,
                    page_title='',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=user_agent[:500],
                    referrer=request.META.get('HTTP_REFERER', ''),
                    device_type=device,
                    session_id=session_id,
                )
            except:
                pass
        
        return response
