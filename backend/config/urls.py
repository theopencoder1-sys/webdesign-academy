from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

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
    path('community/', include('apps.community.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
