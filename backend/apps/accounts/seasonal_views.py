from django.shortcuts import render
from django.utils import timezone
from datetime import date

def get_seasonal_theme():
    """Returns current seasonal theme based on date"""
    today = date.today()
    month = today.month
    day = today.day
    
    themes = {
        'new_year': {'name': 'New Year 2026', 'emoji': '🎉', 'color': '#FFD700', 'start': (1,1), 'end': (1,5)},
        'valentines': {'name': 'Valentine\'s Day', 'emoji': '❤️', 'color': '#FF6B8A', 'start': (2,10), 'end': (2,15)},
        'easter': {'name': 'Easter', 'emoji': '🐣', 'color': '#C8A2FF', 'start': (4,1), 'end': (4,20)},
        'ramadan': {'name': 'Ramadan', 'emoji': '🌙', 'color': '#1B7340', 'start': (3,1), 'end': (3,30)},
        'madaraka': {'name': 'Madaraka Day 🇰🇪', 'emoji': '🇰🇪', 'color': '#000000', 'start': (6,1), 'end': (6,1)},
        'world_cup': {'name': 'World Cup', 'emoji': '⚽', 'color': '#1B7340', 'start': (6,11), 'end': (7,19)},
        'christmas': {'name': 'Christmas', 'emoji': '🎄', 'color': '#DC143C', 'start': (12,1), 'end': (12,31)},
        'mashujaa': {'name': 'Mashujaa Day 🇰🇪', 'emoji': '🦸', 'color': '#C8A2FF', 'start': (10,20), 'end': (10,20)},
        'jamhuri': {'name': 'Jamhuri Day 🇰🇪', 'emoji': '🇰🇪', 'color': '#006600', 'start': (12,12), 'end': (12,12)},
    }
    
    for key, theme in themes.items():
        start_m, start_d = theme['start']
        end_m, end_d = theme['end']
        start_date = date(today.year, start_m, start_d)
        end_date = date(today.year, end_m, end_d)
        
        if start_date <= today <= end_date:
            return theme
    
    return None

def seasonal_banner(request):
    theme = get_seasonal_theme()
    return {'seasonal_theme': theme}
