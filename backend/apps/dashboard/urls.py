from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin-stats/', views.admin_stats, name='admin_stats'),
]
