from django.urls import path
from . import views, api_views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    
    # API endpoints
    path('api/', api_views.assignment_api, name='assignment_api'), # handled by /api/assignments/
    path('api/<int:pk>/update/', api_views.assignment_api, name='assignment_update'),
]
