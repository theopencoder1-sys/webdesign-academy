from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.courses import search_views
from apps.accounts import leaderboard_views
from apps.mentorship import views as mentorship_views
from apps.accounts import broadcast_views, broadcast_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('courses/', include('apps.courses.urls')),
    path('auth/', include('apps.accounts.urls')),
    path('playground/', include('apps.playground.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('mpesa/', include('apps.mpesa.urls')),
    path('pricing/', include('apps.subscriptions.urls')),
    path('projects/', include('apps.projects.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    
    path('career/roadmap/', TemplateView.as_view(template_name='career/roadmap.html'), name='career_roadmap'),
    path('career/interview/', TemplateView.as_view(template_name='career/interview.html'), name='interview_prep'),
    path('career/resume/', TemplateView.as_view(template_name='career/resume.html'), name='resume_templates'),
    path('career/freelance/', TemplateView.as_view(template_name='career/freelance.html'), name='freelance_guide'),
    path('career/pro-hub/', TemplateView.as_view(template_name='career/pro_hub.html'), name='pro_hub'),

    path('quiz/', include('apps.quiz.urls')),
    path('admin/broadcast/', broadcast_views.broadcast_email, name='broadcast_email'),
    path('verify-certificate/', TemplateView.as_view(template_name='certificate_verify.html'), name='verify_certificate'),
    path('mentorship/', include('apps.mentorship.urls')),
    path('leaderboard/', leaderboard_views.leaderboard, name='leaderboard'),
    path('cheatsheets/', TemplateView.as_view(template_name='cheatsheets.html'), name='cheatsheets'),
    path('blog/', TemplateView.as_view(template_name='blog/list.html'), name='blog'),
    path('search/', search_views.search, name='search'),
    path('community/', include('apps.community.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
