# generic/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab  # Asegúrate de importar crontab para programaciones periódicas

# Establece el módulo de configuración de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'generic.settings')

app = Celery('generic')

# Carga las configuraciones de Django en Celery
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 5,
    'interval_start': 0,
    'interval_step': 2,
    'interval_max': 15,
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True