from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenge_list, name='challenge_list'),
    path('submit/<uuid:challenge_id>/', views.submit_challenge, name='submit_challenge'),
]
