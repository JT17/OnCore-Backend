import datetime
from sqlalchemy import desc

from speranza.models import Appointment, Patient
from speranza.util.plivo_messenger import send_message
from speranza.util import is_number
from speranza.util.logger import logger


'''
General Thoughts on changes we will need to make:

There are a few different types of reminders.
    - Post-Appointment reminders that continue for awhile after an appointment
    - Pre-Appointment reminders that go for awhile until an appointment
    - General-Purpose reminders, like for diabetes patients

In order to accomodate General-Purpose reminders, we will need to allow physicians to add custom tags
to patients ('Olga is diabetic'). If the doctor does nothing further, they will receive the Speranza
default reminder texts. If the doctor wants to make a custom schedule for texts, they should be able to
do that - it should get stored in the database. So we need to make a
'''

def send_general_reminders():
    processed_appointments = set()
    general_reminder_sender = GeneralReminderSender()
    all_appts = Appointment.query.order_by(desc(Appointment.date)).all()
    logger.info('# APPOINTMENTS: ', len(all_appts))
    for appt in all_appts:
        try:
            # TODO this way of categorizing patients based on appointments isn't correct.
            # We should update the model to allow custom tags for patient types, and templates in the db
            # that the doctors can easily make scheduled messages for any arbitrary patient type
            appt_type = str(appt.appt_type).upper().replace(" ", "")
            user_id = appt.user_id

            # Don't want to send duplicate messages
            if (appt_type, user_id) not in processed_appointments:
                if (appt_type == 'NOINSULINA' and ('INSULINA', user_id) in processed_appointments) or \
                        (appt_type == 'INSULINA' and ('NOINSULINA', user_id) in processed_appointments):
                    continue

                general_reminder_sender.send_reminder(appt)
                processed_appointments.add((appt_type, user_id))
        except Exception:
            logger.exception("send_general_reminder exception")

    logger.info("# sent_messages: ", len(processed_appointments))
    logger.info(sorted(processed_appointments, key=lambda message: message[1]))


class GeneralReminderSender:
    def __init__(self):

        self.APPOINTMENT_TYPES = {
            'NOINSULINA': self.no_insulina,
            'INSULINA': self.insulina,
            'CHOP': self.chop,
            'GEMOXYABVD': self.gemoxyabvd,
            'ESHAP': self.eshap,
            'ICEYVIPD': self.iceyvipd,
            'MERIDARADIOTERAPIA': self.merida_radioterapia,
            'MERIDAQUIMOTERAPIA': self.merida_quimoterapia,
            'MERIDACUIDADOSPALEATIVOS': self.merida_cuidados_paleativos,
            'MERIDASEGUIMIENTO': self.merida_seguimiento
        }

        self.radiation_messages = {'0': [11, 14, 20], '1': [15, 21, 23], '2': [16, 18, 23],
                                   '3': [17, 21], '4': [24, 14, 23],
                                   '5': [18, 20], '6': [21, 23]}
        self.chemo_messages = {'0': [29, 25], '1': [34, 27, 26], '2': [30, 28], '3': [31, 32],
                               '4': [33, 26], '5': [28], '6': [32]}
        self.pall_messages = {'0': [35, 36], '1': [36], '2': [36, 37], '3': [36],
                              '4': [36, 38], '5': [36], '6': [36]}
        self.follow_messages = {'0': [40, 41], '1': [], '2': [39], '3': [], '4': [], '5': [], '6': []}
        self.monthly = [29, 34, 40]

        merida_messages_file = open('text_files_todo_refactor/merida_mensajes.txt', 'r')
        self.merida_messages = {}
        for line in merida_messages_file:
            if is_number(line):
                self.merida_messages[int(line)] = next(merida_messages_file)

        hemeonc_messages_file = open('text_files_todo_refactor/hemeonc_reminders.txt', 'r')
        self.hemeonc_messages = {}
        treatment = ""
        for line in hemeonc_messages_file:
            if line.rstrip('\n') == 'TREATMENT_TYPE':
                treatment = next(hemeonc_messages_file).rstrip('\n').lower()
                treatment_messages = {}
            elif is_number(line):
                t_message = next(hemeonc_messages_file)
                treatment_messages[int(line)] = t_message
            elif line.rstrip('\n') == 'END_TREATMENT':
                self.hemeonc_messages[treatment] = treatment_messages

    def send_reminder(self, appt):
        # Check that the appointment type exists
        appt_type = str(appt.appt_type).upper().replace(" ", "")
        if appt_type not in self.APPOINTMENT_TYPES:
            logger.error("ILL-FORMATTED APPOINTMENT TYPE PLEASE FIX ME: {0}".format(appt_type))
            return

        try:
            patient = Patient.query.filter(Patient.id == appt.user_id).first()
            reminder_sent = self.APPOINTMENT_TYPES[appt_type](appt, patient)
            logger.info('reminder sent?: [{0}]'.format(reminder_sent))
        except Exception:
            logger.exception('exception in send_reminder')

    # DIABETES REMINDERS
    def no_insulina(self, appt, patient):
        logger.info('called no_insulina')
        message = "Hi {0}, \n realice su dieta, no olvide comer fruitas y verduras cada dia" \
            .format(str(patient.firstname.encode('ascii', 'ignore')))
        return send_message(message, patient.phone_number)

    def insulina(self, appt, patient):
        logger.info('called insulina')
        message = "Hi {0}, \n no olvide que necesita injectarse su insulina hoy, " \
                  "30 minutos antes de tu desayuno y cena".format(str(patient.firstname.encode('ascii', 'ignore')))
        return send_message(message, patient.phone_number)

    # HEMEONC REMINDERS
    def hemeonc_reminder(self, appt, patient, treatment):
        try:
            messages = self.hemeonc_messages[treatment]
        except KeyError:
            logger.error('no matching treatment in hemeonc_reminders for [{0}]'.format(treatment))
            return False

        days_since = (datetime.datetime.today() - appt.date).days
        logger.info("days_since: [{0}] in treatment [{1}]".format(str(days_since), treatment))

        if int(days_since) in self.hemeonc_messages[treatment]:
            logger.info("days_since match in treatment [{0}]".format(treatment))
            patient = Patient.query.filter(Patient.id == appt.user_id).first()
            message = messages[int(days_since)]
            return send_message(message, patient.phone_number)
        else:
            logger.info("no days since match in treatment [{0}]".format(treatment))
            return False

    def gemoxyabvd(self, appt, patient):
        logger.info('called gemoxyabvd')
        return self.hemeonc_reminder(appt, patient, 'gemoxyabvd')

    def chop(self, appt, patient):
        logger.info('called chop')
        return self.hemeonc_reminder(appt, patient, 'chop')

    def eshap(self, appt, patient):
        logger.info('called eshap')
        return self.hemeonc_reminder(appt, patient, 'eshap')

    def iceyvipd(self, appt, patient):
        logger.info('called iceyvipd')
        return self.hemeonc_reminder(appt, patient, 'iceyvipd')

    # MERIDA REMINDERS
    def merida_radioterapia(self, appt, patient):
        logger.info('called merida_radioterapia')
        vals = self.radiation_messages.get(str(datetime.datetime.today().weekday))
        if not vals:
            logger.info("no matching days in merida_radioterapia")
            return True
        for val in vals:
            send_message(self.merida_messages[val], patient.phone_number)
        return True

    def merida_quimoterapia(self, appt, patient):
        logger.info('called merida_quimoterapia')
        vals = self.chemo_messages.get(str(datetime.datetime.today().weekday))
        if not vals:
            logger.info("no matching days in merida_quimoterapia")
            return True
        for val in vals:
            send_message(self.merida_messages[val], patient.phone_number)
        return True

    def merida_cuidados_paleativos(self, appt, patient):
        logger.info('called merida_cuidados_paleativos')
        vals = self.pall_messages.get(str(datetime.datetime.today().weekday))
        if not vals:
            logger.info("no matching days in merida_cuidados_paleativos")
            return True
        for val in vals:
            send_message(self.merida_messages[val], patient.phone_number)
        return True

    def merida_seguimiento(self, appt, patient):
        logger.info('called inmerida_seguimiento')
        vals = self.follow_messages.get(str(datetime.datetime.today().weekday))
        if not vals:
            logger.info("no matching days in merida_seguimiento")
            return True
        for val in vals:
            send_message(self.merida_messages[val], patient.phone_number)

        day_of_month = datetime.datetime.today().day
        if day_of_month == 1:
            send_message(self.merida_messages[self.monthly[0]], patient.phone_number)
        elif day_of_month == 11:
            send_message(self.merida_messages[self.monthly[1]], patient.phone_number)
        elif day_of_month == 21:
            send_message(self.merida_messages[self.monthly[2]], patient.phone_number)
        return True


if __name__ == '__main__':
    send_general_reminders()
