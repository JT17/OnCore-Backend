from flask import abort

from speranza.mod_managers.models import Manager
from speranza.api.common import add_address, get_form_data, sanitize_phone_number, verify_new_user
from speranza import db


def verify_manager_access(patient, auth):
    manager = Manager.query.filter(Manager.id == int(auth.username)).first()
    return patient.grant_access(manager.org_id)


def get_all_managers():
    """Returns all managers"""
    return Manager.query.all()


def add_manager(request, DEBUG=False):
	res = {'msg':'Something has gone wrong'}
	form_data = get_form_data(request, DEBUG)

	requirements = ['firstname', 'lastname', 'password', 'phone_number', 'email']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	if verify_new_user(form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")

	phone_number = sanitize_phone_number(form_data['phone_number'])
	manager = Manager(form_data['firstname'], form_data['lastname'],
		       	phone_number, form_data['email'], form_data['password'])
	try:
		db.session.add(manager)
		db.session.commit()
		if DEBUG == False:
			mp.track(manager.id, "Manager added", properties={'firstname':form_data['firstname'], 'lastname':form_data['lastname']})
	except ValueError as err:
		db.session.flush()
		abort(500, str(err.args))

	res['msg'] = 'success'
	res['mgr_id'] = manager.id
	return res

