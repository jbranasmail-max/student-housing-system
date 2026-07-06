from django.urls import path
from . import views, api_views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    
    # API endpoints
    path('api/', api_views.payment_api, name='payment_api'), # handled by /api/payments/
    path('api/<int:pk>/update/', api_views.payment_api, name='payment_update'),
]
