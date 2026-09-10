from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('units/', views.unit_list_view, name='units'),
    path('units/add/', views.add_unit_view, name='add_unit'),
    path('units/<int:pk>/', views.unit_detail_view, name='unit_detail'),
    path('units/<int:pk>/edit/', views.edit_unit_view, name='edit_unit'),
    path('units/<int:pk>/delete/', views.delete_unit_view, name='delete_unit'),
    path('directory/', views.resident_directory_view, name='directory'),
    path('residents/add/', views.add_resident_view, name='add_resident'),
    path('residents/<int:pk>/edit/', views.edit_resident_view, name='edit_resident'),
    path('residents/<int:pk>/delete/', views.delete_resident_view, name='delete_resident'),
    path('vehicles/', views.vehicle_list_view, name='vehicles'),
    path('vehicles/add/', views.add_vehicle_view, name='add_vehicle'),
    path('vehicles/<int:pk>/delete/', views.delete_vehicle_view, name='delete_vehicle'),
    path('staff/', views.domestic_staff_list_view, name='staff'),
    path('staff/add/', views.add_domestic_staff_view, name='add_staff'),
    path('staff/<int:pk>/delete/', views.delete_domestic_staff_view, name='delete_staff'),
    path('move-requests/', views.move_requests_view, name='move_requests'),
    path('move-requests/<int:pk>/delete/', views.delete_move_request_view, name='delete_move_request'),
    path('violations/', views.violations_view, name='violations'),
    path('violations/<int:pk>/delete/', views.delete_violation_view, name='delete_violation'),
]
