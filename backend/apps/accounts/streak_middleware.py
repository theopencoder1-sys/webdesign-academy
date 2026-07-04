from django.utils import timezone
import datetime

class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            today = timezone.now().date()
            user = request.user
            
            # Only update once per day
            if user.last_active != today:
                if user.last_active is None:
                    user.streak = 1
                elif user.last_active == today - datetime.timedelta(days=1):
                    user.streak += 1
                else:
                    user.streak = 1
                
                if user.streak > user.longest_streak:
                    user.longest_streak = user.streak
                
                user.last_active = today
                
                # Award small XP for daily visit (only once per day)
                user.xp += 5
                user.level = max(1, 1 + int((user.xp / 100) ** 0.5))
                user.save(update_fields=['streak', 'longest_streak', 'last_active', 'xp', 'level'])
        
        response = self.get_response(request)
        return response
