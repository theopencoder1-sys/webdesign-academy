from django.urls import path
from . import views

urlpatterns = [
    path('stk-push/', views.initiate_stk_push, name='stk_push'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('status/<uuid:payment_id>/', views.check_status, name='payment_status'),
]
