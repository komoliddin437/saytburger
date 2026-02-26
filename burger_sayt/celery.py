import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "burger_sayt.settings")

app = Celery("burger_sayt")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
