from flask import abort, g

from speranza.models import Manager
from speranza.api.common import get_form_data, sanitize_phone_number
from speranza.api.verification import verify_form_data, verify_new_user
from speranza.util.mixpanel_logging import mp
from speranza.application import db


def verify_manager_access(patient, auth):
    manager = Manager.query.filter(Manager.id == int(auth.username)).first()
    return patient.grant_access(manager.org_id)


def verify_password(username, password_or_token):
    mgr = Manager.verify_auth_token(password_or_token)
    if not mgr:
        mgr = Manager.query.filter(Manager.id == username).first()
        if not mgr or not mgr.verify_password(password_or_token):
            return False
    g.manager = mgr
    return True


def get_all_managers():
    """Returns all managers"""
    return Manager.query.all()


def add_manager(request, debug=False):
    res = {'msg': 'Something has gone wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['firstname', 'lastname', 'password', 'phone_number', 'email']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    if not verify_new_user(form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")

    phone_number = sanitize_phone_number(form_data['phone_number'])
    manager = Manager(form_data['firstname'], form_data['lastname'],
                      phone_number, form_data['email'], form_data['password'])
    try:
        db.session.add(manager)
        db.session.commit()
        if not debug:
            mp.track(manager.id, "Manager added",
                     properties={'firstname': form_data['firstname'], 'lastname': form_data['lastname']})
    except ValueError as err:
        db.session.flush()
        abort(500, str(err.args))

    res['msg'] = 'success'
    res['mgr_id'] = manager.id
    return res
