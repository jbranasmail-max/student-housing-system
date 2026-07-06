from django.urls import path
from . import views, api_views

app_name = 'housing'

urlpatterns = [
    path('buildings/', views.building_list, name='buildings'),
    path('rooms/', views.room_list, name='rooms'),
    
    # API endpoints
    path('', api_views.building_api, name='building_api'),
    path('<int:pk>/update/', api_views.building_api, name='building_update'),
    path('rooms/', api_views.room_api, name='room_api'), # This will be /api/rooms/
    path('rooms/<int:pk>/update/', api_views.room_api, name='room_update'),
]
