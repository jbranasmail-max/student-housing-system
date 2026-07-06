from django.urls import path
from . import views, api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/', api_views.dashboard_stats_api, name='stats_api'),
]

