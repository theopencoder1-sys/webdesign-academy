from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('visitors/', views.visitor_log, name='visitor_log'),
]
