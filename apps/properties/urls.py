from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('units/', views.unit_list_view, name='units'),
    path('units/<int:pk>/', views.unit_detail_view, name='unit_detail'),
    path('directory/', views.resident_directory_view, name='directory'),
    path('vehicles/', views.vehicle_list_view, name='vehicles'),
    path('vehicles/add/', views.add_vehicle_view, name='add_vehicle'),
    path('staff/', views.domestic_staff_list_view, name='staff'),
    path('staff/add/', views.add_domestic_staff_view, name='add_staff'),
    path('move-requests/', views.move_requests_view, name='move_requests'),
    path('violations/', views.violations_view, name='violations'),
]
