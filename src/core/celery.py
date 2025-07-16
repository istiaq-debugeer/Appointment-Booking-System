from celery import Celery

from core.app_vars import RABBIT_URL

celery_app = Celery(
    "report-task", broker=RABBIT_URL, backend="rpc://", include=["core.tasks"]
)

celery_app.conf.task_default_queue = "reports-queue"

celery_app.autodiscover_tasks()


CELERY_BEAT_SCHEDULE = {
    "generate-daily-report": {
        "task": "app.tasks.daily_report.generate_daily_report",
        "schedule": crontab(hour=2, minute=0),
    },
    "send-appointment-reminders": {
        "task": "app.tasks.reminder_emails.send_appointment_reminders",
        "schedule": crontab(hour=7, minute=0),
    },
}
