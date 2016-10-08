"""TODO E2E testing and celery task"""

import datetime
from speranza.util.logger import logger

from speranza.models import Appointment, Patient
from speranza.util.plivo_messenger import send_message


def send_appointment_reminders(timeframe=datetime.timedelta(days=1)):
    all_appts = Appointment.query.all()
    for appt in all_appts:
        try:
            if appt.checkin or appt.checkout:
                continue

            # TODO late appointment reminders maybe, once actually checkins work
            time_until_appointment = appt.date - datetime.datetime.now()
            logger.info(str(time_until_appointment))
            if timeframe >= time_until_appointment >= datetime.timedelta(days=0):
                patient = Patient.query.filter(Patient.id == appt.user_id).first()
                message = "Hola {0}, \n no olvide que tiene una cita a las {1}".format(
                    str(patient.firstname.encode('ascii', 'ignore')), str(appt.date))
                logger.info("Message: {0} \nNumber: {1} \nDate: {2}".format(message, patient.phone_number, appt.date))
                send_message(message, patient.phone_number)

        except ValueError:
            print str("Couldn't fetch your appointment something went wrong :(")

if __name__ == '__main__':
    send_appointment_reminders()
