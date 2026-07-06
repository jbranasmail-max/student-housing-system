"""
URL configuration for my_hospaital project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from dashboard import views as dashboard_views
from dashboard.api_views import dashboard_stats_api
from students.views import student_api
from housing.api_views import building_api, room_api
from bookings.api_views import assignment_api
from payments.api_views import payment_api
from support.api_views import complaint_api, maintenance_api
from staff.api_views import staff_api
from core.api_views import payment_method_api

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    
    # Public Landing
    path('', dashboard_views.public_home, name='public_home'),

    # Main App - Single Page (Protected Portal)
    path('portal/', dashboard_views.index, name='index'),
    
    # API endpoints matching new.js expectations
    path('api/students/', student_api, name='student_api'),
    path('api/students/<int:pk>/', student_api, name='student_detail_api'),
    path('api/students/<int:pk>/update/', student_api, name='student_update_api'),
    path('api/students/<int:pk>/delete/', student_api, name='student_delete_api'),

    path('api/buildings/', building_api, name='building_api'),
    path('api/buildings/<int:pk>/', building_api, name='building_detail_api'),
    path('api/buildings/<int:pk>/update/', building_api, name='building_update_api'),
    path('api/buildings/<int:pk>/delete/', building_api, name='building_delete_api'),

    path('api/rooms/', room_api, name='room_api'),
    path('api/rooms/<int:pk>/', room_api, name='room_detail_api'),
    path('api/rooms/<int:pk>/update/', room_api, name='room_update_api'),
    path('api/rooms/<int:pk>/delete/', room_api, name='room_delete_api'),

    path('api/assignments/', assignment_api, name='assignment_api'),
    path('api/assignments/<int:pk>/', assignment_api, name='assignment_detail_api'),
    path('api/assignments/<int:pk>/update/', assignment_api, name='assignment_update_api'),
    path('api/assignments/<int:pk>/delete/', assignment_api, name='assignment_delete_api'),

    path('api/payments/', payment_api, name='payment_api'),
    path('api/payments/<int:pk>/', payment_api, name='payment_detail_api'),
    path('api/payments/<int:pk>/update/', payment_api, name='payment_update_api'),
    path('api/payments/<int:pk>/delete/', payment_api, name='payment_delete_api'),

    path('api/complaints/', complaint_api, name='complaint_api'),
    path('api/complaints/<int:pk>/', complaint_api, name='complaint_detail_api'),
    path('api/complaints/<int:pk>/update/', complaint_api, name='complaint_update_api'),
    path('api/complaints/<int:pk>/delete/', complaint_api, name='complaint_delete_api'),

    path('api/maintenance/', maintenance_api, name='maintenance_api'),
    path('api/maintenance/<int:pk>/', maintenance_api, name='maintenance_detail_api'),
    path('api/maintenance/<int:pk>/update/', maintenance_api, name='maintenance_update_api'),
    path('api/maintenance/<int:pk>/delete/', maintenance_api, name='maintenance_delete_api'),

    path('api/dashboard-stats/', dashboard_stats_api, name='dashboard_stats_api'),

    path('api/staff/', staff_api, name='staff_api'),
    path('api/staff/<int:pk>/', staff_api, name='staff_detail_api'),
    path('api/staff/<int:pk>/update/', staff_api, name='staff_update_api'),
    path('api/staff/<int:pk>/delete/', staff_api, name='staff_delete_api'),

    path('api/payment-methods/', payment_method_api, name='payment_method_api'),
    path('api/payment-methods/<int:pk>/', payment_method_api, name='payment_method_detail_api'),
    path('api/payment-methods/<int:pk>/update/', payment_method_api, name='payment_method_update_api'),
    path('api/payment-methods/<int:pk>/delete/', payment_method_api, name='payment_method_delete_api'),
]


    
