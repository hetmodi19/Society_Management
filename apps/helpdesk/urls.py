from django.urls import path
from . import views

app_name = 'helpdesk'

urlpatterns = [
    path('tickets/', views.ticket_list_view, name='tickets'),
    path('tickets/create/', views.create_ticket_view, name='create'),
    path('tickets/<int:pk>/', views.ticket_detail_view, name='detail'),
    path('tickets/<int:pk>/status/', views.update_ticket_status_view, name='update_status'),
    path('tickets/<int:pk>/rate/', views.rate_ticket_view, name='rate'),
    path('tickets/<int:pk>/delete/', views.delete_ticket_view, name='delete_ticket'),
    path('comments/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
]
