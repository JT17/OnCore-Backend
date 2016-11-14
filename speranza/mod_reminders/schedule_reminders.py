from celery import Celery

from speranza.mod_reminders.send_appointment_reminders import send_appointment_reminders
from speranza.mod_reminders.send_general_reminders import send_general_reminders

celery = Celery('send_reminders')
celery.config_from_object('celeryconfig')


@celery.task
def scheduled_run_general():
    send_general_reminders()


@celery.task
def scheduled_run_appointment():
    send_appointment_reminders()
