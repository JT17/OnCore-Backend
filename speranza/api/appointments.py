from flask import abort
import datetime

import sqlalchemy.exc

from speranza.api.common import get_form_data
from speranza.api.verification import verify_form_data, verify_patient_exists, verify_manager_access
from speranza.models import Appointment, Patient, Manager, SurveyResult
from speranza.util.mixpanel_logging import mp
from speranza.application import db


def get_all_appts():
    """Returns all appointments (god view)"""
    return Appointment.query.all()


# TODO
def get_patient_appts(request, debug=False):
    form_data = get_form_data(request, debug)

    res = {'msg': 'Sorry something went wrong'}
    auth = request.authorization
    today = datetime.date.today()
    requirements = ["patient_id"]
    if verify_form_data(requirements, form_data):
        manager = Manager.query.filter(Manager.id == auth.username).first()
        if manager is None:
            abort(422, "La identificacion del gerente es incorecto, intenta otra vez por favor")
        patient_exists = Patient.query.filter(Patient.id == form_data['patient_id']).first()
        if patient_exists is None:
            abort(422, "La identificacion del paciente no existe, intenta otra vez por favor")
        if patient_exists.grant_access(manager.org_id) == False:
            abort(401, "La gerente es incorecto, intenta otra vez por favor")
        ser_appts = []
        try:
            appts = Appointment.query.filter(
                Appointment.date >= today).filter(Appointment.patient_id == form_data["patient_id"]).order_by(Appointment.date).all()
            for appt in appts:
                ser_appts.append(appt.serialize)

        except ValueError, e:
            db.session.rollback()
            abort(500, str(e))
        if len(ser_appts) > 3:
            ser_appts = ser_appts[:3]
        res['msg'] = 'success'
        res['appts'] = ser_appts
        return res
    else:
        abort(422, "Necesitamos mas informacion, intenta otra vez por favor")


def get_manager_appts(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)
    requirements = []
    if verify_form_data(requirements, form_data):
        manager_id = request.authorization.username

        manager_exists = Manager.query.filter(Manager.id == manager_id).first()
        if manager_exists is None:
            abort(422, "La identificacion del gerente es incorrecto, intenta otra vez por favor")
        else:
            appts = Appointment.query.filter(Appointment.manager_id == manager_id).all()
            appt_list = []
            for appt in appts:
                appt_list.append(appt.serialize)
            res['appts'] = appt_list
            res['msg'] = 'success'
        return res
    else:
        abort(422, "Necesitamos mas informacion, intenta otra vez por favor")


def add_appt(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)
    requirements = ['user_id', 'date', 'appt_type']
    if verify_form_data(requirements, form_data):
        # error check that manager making appt is the patient's manager
        print form_data['user_id']
        if verify_patient_exists(form_data['user_id']) is False:
            print "patient doesn't exist"
            abort(422, "La identificacion del paciente es incorrecto")
        if len(form_data['appt_type']) == 0:
            print "appt type is fucked up"
            abort(422, "El appt_type es incorrecto")

        if not verify_manager_access(form_data['user_id'], request.authorization):
            abort(401, "La identificacion del gerente es incorrecto")
        try:
            # right now storing everything as a datetime, but we need to be consistent about this
            timestamp = datetime.datetime.utcfromtimestamp(int(float((form_data['date']))))
            exists = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(
                Appointment.date == timestamp)

            if exists.first() is not None:
                print "there's already an appointment for this date: "
                print timestamp
                abort(422, "Ya existe una cita para este fecha")

            new_appt = Appointment(form_data['user_id'], int(request.authorization.username), timestamp,
                                   form_data['appt_type'])
            db.session.add(new_appt)
            db.session.commit()
            res['msg'] = 'success'
            if not debug:
                mp.track(form_data['user_id'], "New appointment added",
                         properties={'date': timestamp, 'appt_type': form_data['appt_type']})
        except sqlalchemy.exc.DatabaseError, e:
            db.session.rollback()
            abort(500, str(e))
        # db.session.flush();
        return res
    else:
        abort(422, "Necesitamos mas informacion, intenta otra vez por favor")


def edit_appt(request, debug=False):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request, debug)
    requirements = ['user_id', 'old_date']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    else:
        timestamp = datetime.datetime.utcfromtimestamp(int(form_data['old_date']))
        appt = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(
            Appointment.date == timestamp).first()
        if appt is None:
            abort(422, "No hay una cita para este paciente y fecha")
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


def delete_appt(request, debug=False):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['user_id', 'date']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    else:
        timestamp = datetime.datetime.utcfromtimestamp(int(form_data['date']))
        appt = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(
            Appointment.date == timestamp)
        if appt.first() is None:
            abort(422, "No hay una cita para este paciente y fecha")
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
    form_data = get_form_data(request, debug)
    requirements = ['user_id', 'appt_id', 'survey_results']
    if verify_form_data(requirements, form_data):
        if not verify_patient_exists(form_data['user_id']):
            abort(422, "La identificacion del paciente es incorrecto")
        if not verify_manager_access(form_data['user_id'], request.authorization):
            abort(401, "La identificacion del gerente es incorrecto")

        try:
            #timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
            appt = Appointment.query.filter(Appointment.id == form_data['appt_id']).first()
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
                    mp.track(form_data['user_id'], "Patient checked in", properties={'appt_id': form_data['appt_id']})
                else:
                    mp.track(form_data['user_id'], "Patient checked out", properties={'appt_id': form_data['appt_id']})
            manager = Manager.query.filter(Manager.id == request.authorization.username).first()

            #this should never be the case but it isn't worth failing if they've gotten here and no idea why this would ever fail
            if(manager.org_id is not None):
                for survey_res in form_data['survey_results']:
                    new_res = SurveyResult(manager.org_id, survey_res['question'], survey_res['result'])
                    db.session.add(new_res)
                    print "success"
                db.session.commit()
            print res
            return res
        except sqlalchemy.exc.DatabaseError, e:
            abort(500, str(e))
    else:
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
