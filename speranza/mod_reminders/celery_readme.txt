This file contains instructions to run celery crontab module.

Running in the foregroud: (tested)

1. Run celery beat:

celery -A schedule_reminders beat --loglevel=info

2. Run celery work threads:

celery -A schedule_reminders worker -Q celery --loglevel=info
celery -A schedule_reminders worker -Q general_reminder --loglevel=info

Running in the background: (not tested)

1. Run celery beat:

celery -A schedule_reminders beat --loglevel=info &

2. Run worker threads:

celeryd