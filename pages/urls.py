from django.urls import path
from . import views


urlpatterns = [
    # الصفحة الرئيسية
    path('home/', views.index, name='index'),
    
    # API عام للنماذج
    path('api/<str:model_name>/', views.model_api, name='model_api'),
    path('api/<str:model_name>/<int:obj_id>/', views.model_api, name='model_api_with_id'),
    path('api/<str:model_name>/<int:obj_id>/update/', views.model_api, name='model_api_update'),
    path('api/<str:model_name>/<int:obj_id>/delete/', views.model_api, name='model_api_delete'),
    
    # API لإحصائيات لوحة التحكم
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]


