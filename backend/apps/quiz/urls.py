from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('take/<uuid:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('results/', views.quiz_results, name='quiz_results'),
]
