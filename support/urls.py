from django.urls import path
from . import views, api_views

app_name = 'support'

urlpatterns = [
    path('complaints/', views.complaint_list, name='complaints'),
    path('maintenance/', views.maintenance_list, name='maintenance'),
    
    # API endpoints
    path('', api_views.complaint_api, name='complaint_api'), # handled by /api/complaints/
    path('<int:pk>/update/', api_views.complaint_api, name='complaint_update'),
    path('maintenance/', api_views.maintenance_api, name='maintenance_api'), # handled by /api/maintenance/
    path('maintenance/<int:pk>/update/', api_views.maintenance_api, name='maintenance_update'),
]
