from django.urls import path
from . import views

urlpatterns = [
    path('', views.playground, name='playground'),
    path('ai-review/', views.ai_review_api, name='ai_review'),
]
