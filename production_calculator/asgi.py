"""
ASGI config for production_calculator project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'production_calculator.settings')

application = get_asgi_application()