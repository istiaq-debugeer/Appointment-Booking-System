from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os
from settings import settings

load_dotenv()


# RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672//")
redis_url = settings.REDIS_URL

celery_app = Celery(
    "report-task",
    broker=redis_url,
    backend="rpc://",
    include=["tasks"],
)

celery_app.conf.task_default_queue = "reports-queue"

# Beat schedule
celery_app.conf.beat_schedule = {
    "generate-daily-report": {
        "task": "tasks.daily_report.generate_daily_report",
        "schedule": crontab(hour=2, minute=0),
    },
    "send-appointment-reminders": {
        "task": "tasks.reminder_emails.send_appointment_reminders",
        "schedule": crontab(hour=7, minute=0),
    },
}

celery_app.autodiscover_tasks()
