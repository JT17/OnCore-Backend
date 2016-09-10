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


def add_manager(request):
    res = {'msg': 'Something has gone wrong'}
    form_data = get_form_data(request)

    verify_new_user(request)
    try:
        addr = add_address(request)
        if addr is None:
            abort(500, "Hay una problema con el server, por favor intenta otra vez")
    except ValueError as err:
        abort(500, str(err.args))

    if 'password' in form_data:
        phone_number = sanitize_phone_number(form_data['phone_number'])
        contact_number = sanitize_phone_number(form_data['contact_number'])
        manager = Manager(form_data['firstname'], form_data['lastname'],
                          phone_number, contact_number, form_data['password'])
        try:
            db.session.add(manager)
            db.session.commit()
        except ValueError as err:
            db.session.flush()
            abort(500, str(err.args))

        res['msg'] = 'success'
        res['mgr_id'] = manager.id
        return res
    else:
        # TODO check spanish for password
        abort(422, "Necesita una contrasena")
