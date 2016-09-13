from flask import abort

from speranza.models import Address, Manager, Patient, Organization
from speranza.api.verification import verify_form_data, verify_manager_access, verify_new_user
from speranza.api.common import get_form_data, sanitize_phone_number
from speranza.api.addresses import add_address
from speranza.util.mixpanel_logging import mp
from speranza.application import db


def get_patients():
    """Returns all patients"""
    return Patient.query.all()


def find_patient(request, debug=False):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request, debug)
    patients = []
    if 'firstname' in form_data and 'lastname' in form_data and 'dob' in form_data:
        patients = Patient.query.filter(Patient.firstname == form_data['firstname']).filter(
            Patient.lastname == form_data['lastname']).filter(Patient.dob == form_data['dob'])
    elif 'gov_id' in form_data:
        patients = Patient.query.filter(Patient.gov_id == int(form_data['gov_id']))
    else:
        abort(422, 'Necesitamos mas informacion sobre el paciente, por favor hacer otra vez')

    mgr_patients = []
    for patient in patients:
        if verify_manager_access(patient.id, request.authorization):
            mgr_patients.append(patient)

    if len(mgr_patients) == 0:
        abort(422, "No hay pacientes con este informacion")

    res['msg'] = 'success'
    res['patients'] = mgr_patients
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


def add_patient(request, debug=False):
    res = {'msg': 'something went wrong sorry'}
    form_data = get_form_data(request, debug)
    required_args = ['firstname', 'lastname', 'phone_number', 'contact_number', 'dob', 'gov_id', 'city_name']
    if not verify_form_data(required_args, form_data):
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
        if manager is not None:
            abort(401, 'La identificacion para el gerente es incorecto, por favor intenta otra vez')
        else:
            # right now storing everything as a datetime, but we need to be consistent about this
            # dob = datetime.datetime.utcfromtimestamp(float(form_data['dob']));
            patient_phone_number = sanitize_phone_number(form_data['phone_number'])
            patient_contact_number = sanitize_phone_number(form_data['contact_number'])
            patient = Patient(form_data['firstname'], form_data['lastname'], patient_phone_number,
                              patient_contact_number, patient_addr.id, form_data['dob'], form_data['gov_id'])
            # message = client.messages.create(to=form_data['phone_number'],
            # from_=form_data['phone_number'],body=add_patient_message)
            # message = "Gracias para unir Speranza Health"

            # r = send_message(message, patient.contact_number, debug)
            # print r

            # add patient to organization
            manager_org = Organization.query.filter(Organization.id == manager.org_id).first()
            patient.organizations.append(manager_org)

            try:
                db.session.add(patient)
                db.session.commit()
                if not debug:
                    mp.track(auth.username, "Patient added",
                             properties={'firstname': form_data['firstname'], 'lastname': form_data['lastname'],
                                         'dob': form_data['dob'], 'gov_id': form_data['gov_id']})
            except Exception, e:
                abort(500, str(e))

            res['msg'] = 'success'
            res['patient_id'] = patient.id
            res['patient_contact_number'] = patient.contact_number
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
    if verify_manager_access(user.first().id, auth):
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
