from flask import abort

from speranza.mod_addresses.models import Address
from speranza.mod_managers.models import Manager
from speranza.mod_patients.models import Patient
from speranza.api.addresses import edit_patient_address
from speranza.api.common import add_address, get_form_data, sanitize_phone_number, verify_new_user
from speranza.api.managers import verify_manager_access
from speranza.util.plivo_messenger import send_message
from speranza.util.mixpanel_logging import mp
from speranza import db


def get_patients():
    """Returns all patients"""
    return Patient.query.all()


def find_patient(request):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request)
    patients = []
    if 'firstname' in form_data and 'lastname' in form_data and 'dob' in form_data:
        patients = Patient.query.filter(Patient.firstname == form_data['firstname']).filter(
            Patient.lastname == form_data['lastname']).filter(Patient.dob == form_data['dob'])
    elif 'gov_id' in form_data:
        patients = Patient.query.filter(Patient.gov_id == int(form_data['gov_id']))
    else:
        abort(422, 'Necesitamos mas informacion sobre el paciente, por favor hacer otra vez')

    ser_patients = []
    for patient in patients:
        address = Address.query.filter(Address.id == patient.address_id).first()
        manager = Manager.query.filter(Manager.id == patient.manager_id).first()
        ser_pt = {'firstname': patient.firstname, 'lastname': patient.lastname, 'phone_number': patient.phone_number,
                  'contact_number': patient.contact_number, 'street_num': address.street_num,
                  'street_name': address.street_name,
                  'street_type': address.street_type, 'city_name': address.city_name, 'zipcode': address.zipcode,
                  'district': address.district,
                  'manager_firstname': manager.firstname, 'manager_lastname': manager.lastname,
                  'manager_phone_number': manager.phone_number,
                  'manager_contact_number': manager.contact_number, 'dob': patient.dob, 'gov_id': patient.gov_id,
                  'patient_id': patient.id}
        ser_patients.append(ser_pt)

    if len(ser_patients) == 0:
        abort(422, "No hay pacientes con este informacion")

    res['msg'] = 'success'
    res['patients'] = ser_patients
    return res


def add_patient(request, debug=False):
    res = {'msg': 'something went wrong sorry'}
    form_data = get_form_data(request)
    verify_new_user(request)
    if 'dob' not in form_data:
        abort(422, 'Necesita dob, intenta otra vez')
    if 'gov_id' not in form_data:
        abort(422, 'Necesita identificacion, intenta otra vez')
    patient_addr = Address()
    try:
        patient_addr = add_address(request)
        if patient_addr is None:
            abort(500, 'Tenemos una problema con la aplicacion, por favor intenta otra vez')
    except ValueError as err:
        abort(500, str(err.args))
    auth = request.authorization
    if auth.username:
        manager = Manager.query.filter(Manager.id == int(auth.username))
        if manager is None:
            abort(401, 'La identificacion para el gerente es incorecto, por favor intenta otra vez')
        else:
            try:
                # right now storing everything as a datetime, but we need to be consistent about this
                # dob = datetime.datetime.utcfromtimestamp(float(form_data['dob']))
                patient_phone_number = sanitize_phone_number(form_data['phone_number'])
                patient_contact_number = sanitize_phone_number(form_data['contact_number'])
                patient = Patient(form_data['firstname'], form_data['lastname'], patient_phone_number,
                                  patient_contact_number, patient_addr.id, form_data['dob'],
                                  form_data['gov_id'])

                # message = client.messages.create(to=form_data['phone_number'],
                # from_=form_data['phone_number'],body=add_patient_message)
                message = "Gracias para unir Speranza Health"

                # TODO log response, or send alert to slack or something
                r = send_message(message, patient.contact_number)
                print r

                # add patient to organization
                patient.organizations.append(manager.org_id)

                db.session.add(patient)
                db.session.commit()

                if not debug:
                    mp.track(manager.id, "Manager added",
                             properties={'firstname': form_data['firstname'], 'lastname': form_data['lastname']})

                res['msg'] = 'success'
                res['patient_id'] = patient.id
                res['patient_contact_number'] = patient.contact_number
                # print res
                return res
            except Exception, e:
                db.session.flush()
                abort(500, str(e))


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

            if not verify_manager_access(user, auth):
                abort(422, "Invalid manager")
            if 'phone_number' in form_data:
                if not form_data['phone_number'].isdigit() or (len(form_data['phone_number']) == 0):
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
                db.session.rollback()
                print e
                abort(500, "Something went wrong, couldn't update")
        except ValueError:
            abort(500, "Something went wrong trying to fetch your user_id please try again")


def delete_patient(request):
    res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request)

    if 'user_id' not in form_data:
        abort(422, "No podemos borrar el paciente,  necesitamos la identificacion del usario")
    auth = request.authorization
    user = Patient.query.filter(Patient.id == form_data['user_id'])
    if user.first() is None:
        abort(422, "La identificacion es incorrecto")
    if not verify_manager_access(user, auth):
        abort(422, "La identificacion del gerente es incorrecto")
    try:
        user.delete()
        db.session.commit()
        res['msg'] = 'success'
        return res
    except Exception as e:
        print e
        abort(500, "borrar ha fallado")
