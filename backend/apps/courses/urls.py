from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('html5-full/', views.html_full, name='html_full'),
    path('css-full/', views.css_full, name='css_full'),
    path('javascript-full/', views.javascript_full, name='javascript_full'),
    path('tailwind-full/', views.tailwind_full, name='tailwind_full'),
    path('fullstack-full/', views.fullstack_full, name='fullstack_full'),
    path('python-full/', views.python_full, name='python_full'),
    path('react-full/', views.react_full, name='react_full'),
    path('uiux-full/', views.uiux_full, name='uiux_full'),
    path('cybersecurity-full/', views.cybersecurity_full, name='cybersecurity_full'),
    path('certificate/<slug:course_slug>/', views.certificate, name='certificate'),
    path('<slug:course_slug>/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
]
