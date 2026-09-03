"""
WSGI config for SmartSociety 360 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'society_core.settings')

application = get_wsgi_application()

# Vercel serverless alias
app = application
