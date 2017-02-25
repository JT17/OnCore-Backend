from flask import abort

from speranza.models import Address, Manager, Patient, Organization, TextRegimen
from speranza.api.verification import verify_form_data, verify_manager_access, verify_new_user
from speranza.api.common import get_form_data, sanitize_phone_number
from speranza.api.addresses import add_address
from speranza.application import db
from speranza.util.mixpanel_logging import mp
from speranza.util.plivo_messenger import send_message
import datetime


def get_patients():
    """Returns all patients"""
    return Patient.query.all()


def find_patient(request, debug=False):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request, debug)
    patients = []
    has_data = False
    found_patients = {}
    if 'firstname' in form_data:
        for patient in Patient.query.filter(Patient.firstname == form_data['firstname']).all():
            if patient.id not in found_patients:
                patients.append(patient)
                found_patients[patient.id] = True
        has_data = True
    if 'lastname' in form_data:
        for patient in Patient.query.filter(Patient.lastname == form_data['lastname']).all():
            if patient.id not in found_patients:
                patients.append(patient)
                found_patients[patient.id] = True
        has_data = True
    if 'dob' in form_data:
        for patient in Patient.query.filter(Patient.dob == form_data['dob']).all():
            if patient.id not in found_patients:
                patients.append(patient)
                found_patients[patient.id] = True
        has_data = True
    if 'gov_id' in form_data:
        for patient in Patient.query.filter(Patient.gov_id == int(form_data['gov_id'])).all():
            if patient.id not in found_patients:
                patients.append(patient)
                found_patients[patient.id] = True
        has_data = True
    if has_data is False:
        abort(422, 'Necesitamos mas informacion sobre el paciente, por favor hacer otra vez')

    verified_patients = []
    for patient in patients:
        if verify_manager_access(patient.id, request.authorization):
            verified_patients.append(patient.serialize)

    if len(verified_patients) == 0:
        abort(422, "No hay pacientes con este informacion")

    res['msg'] = 'success'
    res['patients'] = verified_patients
    return res


def edit_patient_address(request, debug=False):
    # res = {'msg':'something has gone wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['user_id']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    else:
        user = Patient.query.filter(Patient.id == form_data['user_id']).first()
        if user is None:
            abort(500, "something went wrong")
        address = Address.query.filter(Address.id == user.address_id).first()
        if address is None:
            abort(500, "Something went wrong fetching the address")
        if 'street_num' in form_data:
            address.street_num = form_data['street_num']
        if 'street_name' in form_data:
            address.street_name = form_data['street_name']
        if 'street_type' in form_data:
            address.street_type = form_data['street_type']
        if 'city_name' in form_data:
            address.city_name = form_data['city_name']
        if 'zipcode' in form_data:
            address.zipcode = form_data['zipcode']
        if 'district' in form_data:
            address.district = form_data['district']
        try:
            db.session.commit()
        except Exception as e:
            print e
            db.session.rollback()
            abort(500, "something went wrong")


def edit_patient(request):
    res = {'msg': "something has gone wrong"}
    form_data = get_form_data(request)

    if 'user_id' not in form_data:
        abort(422, "No podemos editar el paciente, necesita user_id")
    else:
        try:
            auth = request.authorization
            user = Patient.query.filter(Patient.id == form_data['user_id']).first()
            if user is None:
                abort(422, "Invalid patient id")

            if not verify_manager_access(user.id, auth):
                abort(422, "Invalid manager")
            if 'phone_number' in form_data:
                if not form_data['phone_number'].isdigit() or len(form_data['phone_number']) == 0:
                    abort(422, 'Please enter a valid phone number')
                user.phone_number = form_data['phone_number']
            if 'contact_number' in form_data:
                if not form_data['contact_number'].isdigit():
                    abort(422, 'Please enter a valid contact number')
                    return res
                user.contact_number = form_data['contact_number']
            if 'edit_address' in form_data:
                edit_patient_address(request)
            if 'dob' in form_data:
                user.dob = form_data['dob']
            try:
                db.session.commit()
                res['msg'] = "success"
                return res
            except Exception as e:
                print e
                db.session.rollback()
                abort(500, "Something went wrong, couldn't update")
        except ValueError, e:
            print e
            abort(500, "Something went wrong trying to fetch your user_id please try again")


# TODO check for duplicate patients
def add_patient(request, debug=False):
    res = {'msg': 'something went wrong sorry'}
    form_data = get_form_data(request, debug)
    required_args = ['firstname', 'lastname', 'phone_number', 'dob', 'gov_id', 'city_name']
    if not verify_form_data(required_args, form_data):
        print "not enough info"
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    verify_new_user(form_data)
    patient_addr = ''
    try:
        patient_addr = add_address(request)
        if patient_addr is None or patient_addr.id is None:
            abort(500, 'Tenemos una problema con la aplicacion, por favor intenta otra vez')
    except ValueError as err:
        abort(500, str(err.args))
    auth = request.authorization
    if auth.username:
        manager = Manager.query.filter(Manager.id == int(auth.username)).first()
        if manager is None:
            abort(401, 'La identificacion para el gerente es incorecto, por favor intenta otra vez')
        else:
            # right now storing everything as a datetime, but we need to be consistent about this
            # dob = datetime.datetime.utcfromtimestamp(float(form_data['dob']));
            patient_phone_number = sanitize_phone_number(form_data['phone_number'])
            timestamp = datetime.datetime.utcfromtimestamp(int(float((form_data['dob']))))
            if "contact_number" in form_data:
                patient_contact_number = sanitize_phone_number(form_data['contact_number'])

                patient = Patient(firstname=form_data['firstname'],
                                  lastname=form_data['lastname'],
                                  phone_number=patient_phone_number,
                                  contact_number=patient_contact_number,
                                  address_id=patient_addr.id,
                                  dob=timestamp,
                                  gov_id=form_data['gov_id'])
            else:
                patient = Patient(firstname=form_data['firstname'],
                                  lastname=form_data['lastname'],
                                  phone_number=patient_phone_number,
                                  contact_number=None,
                                  address_id=patient_addr.id,
                                  dob=timestamp,
                                  gov_id=form_data['gov_id'])
            # add patient to organization
            manager_org = Organization.query.filter(Organization.id == manager.org_id).first()
            if manager_org:
                patient.organizations.append(manager_org)

            try:
                db.session.add(patient)
                db.session.commit()
                if not debug:
                    mp.track(auth.username, "Patient added",
                             properties={'firstname': form_data['firstname'], 'lastname': form_data['lastname'],
                                         'dob': form_data['dob'], 'gov_id': form_data['gov_id']})
            except Exception, e:
                print e
                abort(500, str(e))

            res['msg'] = 'success'
            res['patient_id'] = patient.id
            res['patient_phone_number'] = patient.phone_number
            res['patient_name'] = patient.firstname + " " + patient.lastname
            res['last_appt_details'] = "Nunca ha tenido una cita"
            message = "Gracias para unir Speranza Health"
            r = send_message(message, patient.phone_number, debug)

            # print res
            return res


def delete_patient(request, debug=False):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['user_id']
    if not verify_form_data(requirements, form_data):
        abort(422, "No podemos borrar el paciente,  necesitamos la identificacion del usario")
    auth = request.authorization
    user = Patient.query.filter(Patient.id == form_data['user_id'])
    if user.first() is None:
        abort(422, "La identificacion es incorrecto")
    if not verify_manager_access(user.first().id, auth):
        abort(422, "La identificacion del gerente es incorrecto")
    try:
        user.delete()
        db.session.commit()
        res['msg'] = 'success'
        return res
    except Exception as e:
        print e
        db.session.rollback()
        abort(500, "borrar ha fallado")

def set_text_regimen(request, debug=False):
    res = {"msg":"something has gone wrong"}
    form_data = get_form_data(request, debug)

    requirements = ['patient_id', 'regimen_id']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesitamos mas informacion, intenta otra vez por favor")
    auth = request.authorization
    if auth is not None:
        manager = Manager.query.filter(Manager.id == auth.username).first()
        if manager is None:
            abort(401, "Este gerente es incorecto, intenta otra vez por favor")
        patient = Patient.query.filter(Patient.id == form_data['patient_id']).first()
        if patient is None:
            abort(422, "Hay una problema con la identificacion del paciente, intenta otra vez por favor")
        regimen_exists = TextRegimen.query.filter(TextRegimen.id == form_data['regimen_id']).first()
        if regimen_exists is None:
            abort(422, "Hay una problema con la identificacion del regimen, intenta otra vez por favor")
        patient.text_regimen_id = regimen_exists.id
        db.session.commit()
        res['msg'] = 'success'
        return res