import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'textrecognition.settings')

app = Celery('textrecognition')
app.config_from_object('django.conf:settings', namespace = 'CELERY')
app.autodiscover_tasks()
