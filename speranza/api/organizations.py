from flask import abort, g

from speranza.models import Organization, Manager
from speranza.api.common import get_form_data, sanitize_phone_number
from speranza.api.verification import verify_form_data, verify_new_user
from speranza.util.mixpanel_logging import mp
from speranza.application import db

def add_organization(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)

    #I think the org_email can be optional
    requirements = ['org_name']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    manager_id = request.authorization.username
    if manager_id is not None:
        manager = Manager.query.filter(Manager.id == manager_id)
        if manager is None:
            abort(401, "La identificacion del gerente es incorrecto")
    else:
        abort(401, "No hay identificacion para el gerente")
    org_exists = Organization.query.filter(Organization.org_name == form_data['org_name'])
    if org_exists is not None:
        abort(422, "Ya existe un organizacion con este nombre, intenta otra vez por favor")

    if 'org_email' in form_data:
        new_org = Organization(org_name=form_data['org_name'], org_email=form_data['org_email'])
    else:
        new_org = Organization(org_name = form_data['org_name'])
    db.session.add(new_org)
    db.session.commit()

    #TODO assumes that the first person is going to be an admin. up for debate in the future
    new_org.add_admin(request.authorization.username)
    res['msg'] = "success"
    res['org'] = new_org.serialize
    return res

#called to give manager access to organization (this is hit by the link we send to the org admins)
def add_manager_to_organization(request, debug=False):
    res = {'msg':'Sorry something went wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['org_id']
    if not verify_form_data(requirements, form_data):
        print "wtf"
        abort(422, "Necesita mas informacion, intenta otra vez por favor")

    mgr_id = request.authorization.username
    if mgr_id is not None:
        manager = Manager.query.filter(Manager.id == mgr_id).first()
        if manager is None:
            abort(401, "La identificacion del gerente es incorrecto")
    else:
        abort(401, "No hay identificacion para el gerente")
    org = Organization.query.filter(Organization.id == form_data['org_id']).first()
    if org is None:
        abort(422, "No hay organizacion con este identificaion, intenta otra vez por favor")

    org.add_manager(mgr_id)
    manager.set_org(form_data['org_id'])
    db.session.commit()
    res['msg'] = "success"
    return res

