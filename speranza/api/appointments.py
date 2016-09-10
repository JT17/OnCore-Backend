from flask import abort
import datetime
import sqlalchemy.exc

from speranza.api.common import get_form_data, verify_form_data
from speranza.api.managers import verify_manager_access
from speranza.mod_patients.models import Patient
from speranza.mod_appointments.models import Appointment
from speranza.util.mixpanel_logging import mp
from speranza import db, auth


def get_all_appts():
    """Returns all appointments (god view)"""
    return Appointment.query.all()


# TODO
def get_patient_appts(request):
    # form_data = get_form_data(request)
    try:
        res = {'msg': 'Sorry something went wrong'}
        import datetime
        today = datetime.date.today()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        # pts = Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id)

        # TODO: broken
        # appts = Appointment.query.filter(Appointment.user_id.in_(Patient.query.filter(
        # Patient.manager_id == int(auth.username)).
        # with_entities(Patient.id))).filter(Appointment.date >= today).filter(Appointment.date < tomorrow).join
        # (Patient, (Patient.id == Appointment.user_id)).with_entities
        # (Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()

        appts = Appointment.query.filter(Appointment.manager_id == int(request.authorization.username)).filter(
            Appointment.date >= today).filter(Appointment.date < tomorrow).join(Patient, (
            Patient.id == Appointment.user_id)).with_entities(
            Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()

        ser_appts = []
        for appt in appts:
            ser_appt = {'firstname': appt.firstname, 'lastname': appt.lastname, 'date': appt.date,
                        'appt_type': appt.appt_type}
            ser_appts.append(ser_appt)

        res['msg'] = 'success'
        res['appts'] = ser_appts
        return res
    except ValueError, e:
        db.session.rollback()
        abort(500, str(e))


# TODO
def get_manager_appts(request):
    print request
    pass


def add_appt(request, debug=False):
    """Adds an appointment"""
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request)

    requirements = ['user_id', 'date', 'appt_type']
    if verify_form_data(requirements, form_data):
        # error check that manager making appt is the patient's manager
        patient = Patient.query.filter(Patient.id == form_data['user_id']).first()
        if patient is None:
            abort(422, "La identificacion del paciente es incorrecto")
        if len(form_data['appt_type']) == 0:
            abort(422, "El appt_type es incorrecto")

        if not verify_manager_access(patient, request.authorization):
            abort(401, "La identificacion del gerente es incorrecto")
        try:
            # right now storing everything as a datetime, but we need to be consistent about this
            timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
            exists = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(
                Appointment.date == timestamp)

            if exists.first() is not None:
                abort(422, "Ya existe una cita para este fecha")

            new_appt = Appointment(form_data['user_id'], int(auth.username), timestamp, form_data['appt_type'])
            db.session.add(new_appt)
            db.session.commit()
            res['msg'] = 'success'
            if not debug:
                mp.track(form_data['user_id'], "New appointment added",
                         properties={'date': timestamp, 'appt_type': form_data['appt_type']})
        except sqlalchemy.exc.DatabaseError, e:
            db.session.rollback()
            abort(500, str(e))
            # db.session.flush()
            return res
        return res
    else:
        abort(422, "Necesitamos mas informacion, intenta otra vez por favor")


def edit_appt(request):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request)

    if 'user_id' not in form_data or 'old_date' not in form_data:
        abort(422, "Could not edit appt, missing user_id or date in form")
    else:
        import datetime
        timestamp = datetime.datetime.utcfromtimestamp(int(form_data['old_date']))
        appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(
            Appointment.date == timestamp).first()
        if appt is None:
            abort(422, "Necesitamos la identificacion del usario o la fecha")
        changed = False
        if 'new_date' in form_data:
            new_timestamp = datetime.datetime.utcfromtimestamp(int(form_data['new_date']))
            appt.date = new_timestamp
            changed = True
        if 'appt_type' in form_data:
            appt.appt_type = form_data['appt_type']
            changed = True
        try:
            if changed:
                db.session.commit()
            res['msg'] = "success"
            return res
        except ValueError, e:
            db.session.rollback()
            abort(500, str(e))


def delete_appt(request):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request)

    if 'user_id' not in form_data or 'date' not in form_data:
        abort(422, "No podemos borrar la cita, necesitamos la identificacion del usario o la fecha")
    else:
        import datetime
        timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
        appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(
            Appointment.date == timestamp)
        if appt.first() is None:
            abort(422, "Necesitamos la identificacion del usario o la fecha")
        try:
            appt.delete()
            db.session.commit()
            res['msg'] = 'success'
            return res
        except ValueError, e:
            db.session.rollback()
            abort(500, str(e))


def checkin_out(request, checkin=True, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request)

    if 'user_id' in form_data and 'date' in form_data:
        patient = Patient.query.filter(Patient.id == form_data['user_id']).first()
        if patient is None:
            abort(422, "La identificacion del paciente es incorrecto")

        if not verify_manager_access(patient, request.authorization):
            abort(401, "La identificacion del gerente es incorrecto")

        try:
            import datetime
            timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
            appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(
                Appointment.date == timestamp).first()
            if appt is None:
                abort(422, "La fecha es incorrecto, intenta otra vez por favor")
            if checkin:
                if appt.checkin:
                    abort(422, "Ya comprobado para este cita")
                appt.checkin = True
            else:
                if appt.checkout:
                    abort(422, "Ya desprotegido")
                appt.checkout = True
            db.session.commit()
            res['msg'] = 'success'

            if not debug:
                if checkin:
                    mp.track(form_data['user_id'], "Patient checked in", properties={'date': timestamp})
                else:
                    mp.track(form_data['user_id'], "Patient checked out", properties={'date': timestamp})

            return res
        except sqlalchemy.exc.DatabaseError, e:
            abort(500, str(e))
    else:
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
