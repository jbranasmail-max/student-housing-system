from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('api/', views.student_api, name='api_create'),
    path('api/<int:pk>/', views.student_api, name='api_detail'),
]
