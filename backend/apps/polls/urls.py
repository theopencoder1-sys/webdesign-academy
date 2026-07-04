from django.urls import path
from . import views

urlpatterns = [
    path('', views.active_polls, name='active_polls'),
    path('vote/<uuid:poll_id>/', views.vote_poll, name='vote_poll'),
    path('create/', views.create_poll, name='create_poll'),
    path('api/latest/', views.latest_poll_api, name='latest_poll_api'),
]
