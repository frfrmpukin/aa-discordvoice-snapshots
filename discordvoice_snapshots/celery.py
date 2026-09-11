from celery import Celery

app = Celery("discordvoice_snapshots")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["discordvoice_snapshots"])
