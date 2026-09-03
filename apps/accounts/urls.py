from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('security/', views.security_settings_view, name='security'),
    path('demo-switch/<str:role>/', views.demo_switch_user, name='demo_switch'),
]
