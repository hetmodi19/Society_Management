from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # App routers
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('properties/', include('apps.properties.urls', namespace='properties')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('gatekeeper/', include('apps.gatekeeper.urls', namespace='gatekeeper')),
    path('helpdesk/', include('apps.helpdesk.urls', namespace='helpdesk')),
    path('amenities/', include('apps.amenities.urls', namespace='amenities')),
    path('communications/', include('apps.communications.urls', namespace='communications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
