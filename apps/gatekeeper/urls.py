from django.urls import path
from . import views

app_name = 'gatekeeper'

urlpatterns = [
    path('terminal/', views.gate_terminal_view, name='terminal'),
    path('entry/', views.visitor_entry_view, name='entry'),
    path('checkout/<int:pk>/', views.visitor_checkout_view, name='checkout'),
    path('visitor/<int:pk>/delete/', views.delete_visitor_log_view, name='delete_visitor'),
    path('verify-pass/', views.verify_passcode_view, name='verify_pass'),
    path('passes/', views.passes_view, name='passes'),
    path('passes/create/', views.create_pass_view, name='create_pass'),
    path('passes/<int:pk>/delete/', views.delete_pass_view, name='delete_pass'),
    path('parcels/', views.parcel_desk_view, name='parcels'),
    path('parcels/collect/<int:pk>/', views.collect_parcel_view, name='collect_parcel'),
    path('parcels/<int:pk>/delete/', views.delete_parcel_view, name='delete_parcel'),
    path('sos/trigger/', views.trigger_sos_view, name='trigger_sos'),
    path('sos/resolve/<int:pk>/', views.resolve_sos_view, name='resolve_sos'),
]
