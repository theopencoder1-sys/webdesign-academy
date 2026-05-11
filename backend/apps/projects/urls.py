from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('my/', views.my_projects, name='my_projects'),
    path('create/', views.create_project, name='create_project'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
]
