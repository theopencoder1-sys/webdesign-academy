from django.urls import path
from . import views

urlpatterns = [
    path('admin/upload/', views.upload_material, name='upload_material'),
    path('api/<slug:course_slug>/', views.materials_api, name='materials_api'),
    path('<slug:course_slug>/', views.course_materials, name='course_materials'),
]
