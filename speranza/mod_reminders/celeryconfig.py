from celery.schedules import crontab

BROKER_URL = 'sqla+sqlite:///speranza_celery.db'
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = 'sqlite:///speranza_celery.db'
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_TIMEZONE='America/Los_Angeles'

CELERY_DEFAULT_QUEUE = 'celery'

CELERYBEAT_SCHEDULE = {
    'run_appointment': {
        'task': 'schedule_reminders.scheduled_run_appointment',
        'schedule': crontab(minute=0,hour=0, day_of_week='0-6'),
    },
    'run_general': {
        'task': 'schedule_reminders.scheduled_run_general',
        'schedule': crontab(minute=0,hour=0, day_of_week='0-6'),
    },
}

CELERY_ROUTES = {
    'schedule_reminders.scheduled_run_general': {'queue': 'general_reminder'},
}
