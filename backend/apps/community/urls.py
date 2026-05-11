from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('create/', views.create_topic, name='create_topic'),
    path('topic/<uuid:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<uuid:topic_id>/reply/', views.reply_topic, name='reply_topic'),
]
