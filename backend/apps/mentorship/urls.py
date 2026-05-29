from django.urls import path
from . import views
urlpatterns = [
    path('', views.mentorship_hub, name='mentorship_hub'),
    path('book/', views.book_session, name='book_session'),
    path('review/', views.submit_review, name='submit_review'),
]
