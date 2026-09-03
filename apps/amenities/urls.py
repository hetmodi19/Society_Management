from django.urls import path
from . import views

app_name = 'amenities'

urlpatterns = [
    path('', views.amenity_list_view, name='list'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('manage/', views.manage_bookings_view, name='manage'),
    path('ev-charging/', views.ev_charging_view, name='ev_charging'),
    path('cancel/<int:pk>/', views.cancel_booking_view, name='cancel'),
    path('<slug:slug>/', views.amenity_detail_view, name='detail'),
]
