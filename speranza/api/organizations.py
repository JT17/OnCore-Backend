from flask import abort

from speranza.models import Organization, Manager, TextRegimen, Text
from speranza.api.common import get_form_data
from speranza.api.verification import verify_form_data
from speranza.application import db

def get_organizations(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    all_orgs = Organization.query.all()
    serialized_orgs = []
    for org in all_orgs:
        serialized_orgs.append(org.serialize)
    res['msg'] = 'success'
    res['orgs'] = serialized_orgs
    return res


def add_organization(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)

    # I think the org_email can be optional
    requirements = ['org_name']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informaction, intenta otra vez por favor")
    manager_id = request.authorization.username
    if manager_id is not None:
        manager = Manager.query.filter(Manager.id == manager_id).first()
        if manager is None:
            abort(401, "La identificacion del gerente es incorrecto")
    else:
        abort(401, "No hay identificacion para el gerente")
    org_exists1 = Organization.query.filter(Organization.org_name.ilike(form_data['org_name'])).all()
    org_exists = Organization.query.filter(Organization.org_name == form_data['org_name']).all()
    if len(org_exists) != 0 or len(org_exists1) != 0:
        abort(422, "Ya existe un organizacion con este nombre, intenta otra vez por favor")

    if 'org_email' in form_data:
        new_org = Organization(org_name=form_data['org_name'], org_email=form_data['org_email'], org_pwd="TODO")
    else:
        new_org = Organization(org_name=form_data['org_name'], org_pwd="TODO")
    db.session.add(new_org)
    db.session.commit()

    manager.org_id = new_org.id
    new_org.add_admin(request.authorization.username)
    db.session.commit()
    res['msg'] = "success"
    res['org'] = new_org.serialize
    res['org_id'] = new_org.id
    return res


# called to give manager access to organization (this is hit by the link we send to the org admins)
def add_manager_to_organization(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
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
    manager.pending_access = False
    db.session.commit()
    res['msg'] = "success"
    return res

def add_text_regimen(request, debug=False):
    res = {'msg':'Sorry something went wrong'}
    form_data = get_form_data(request, debug)
    requirements = ['text_msgs', 'regimen_name']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informacion, intenta otra vez por favor")

    mgr_id = request.authorization.username
    if mgr_id is None:
        abort(401, "No hay identificacion para el gerente")
    manager = Manager.query.filter(Manager.id == mgr_id).first()
    if manager is None:
        abort(401, "La identificacion del gerente es incorecto")

    manager_org_id = manager.org_id
    if manager_org_id is None:
        abort(422, "Este gerente no esta en un organizacion, por favor intenta con otra gerente")
    existing_regimen = TextRegimen.query.filter(TextRegimen.regimen_name == form_data['regimen_name']).all()
    if len(existing_regimen) != 0:
        abort(422, "Ya existe un regimen con este nombre, por favor intenta con otra nombre")

    regimen_texts = {}
    for text in form_data['text_msgs']:
        print text
        text_exists = Text.query.filter(Text.text_msg == text['msg']).first()
        if( (text['new_text'] == "True") or (text['new_text'] == True)):
            if(text_exists is not None):
                res['already_exists'] = "Ya existe un mensaje con este informacion: {0}. " \
                                        "En la futura, no es necesario anadir el mismo mensaje otra vez".format(text['msg'])
                regimen_texts[text['day']] = text_exists
            else:
                new_text = Text(manager_org_id, text['msg'])
                db.session.add(new_text)
                regimen_texts[text['day']] = new_text
        else:

            if(text_exists is None):
                abort(422, "Este mensaje: {0} no existe, por favor intenta otra vez".format(text['msg']))
            regimen_texts[text['day']] = text_exists
    db.session.commit()
    new_regimen = TextRegimen(manager_org_id, form_data["regimen_name"])
    for day, text in regimen_texts.iteritems():
        if(text.id is None):
            abort(422, "Tenemos una problema, por favor intenta otra vez")
        new_day = new_regimen.add_text(text.id, day)
        if new_day != 1:
            abort(422, "Hay una problema con las mensajes, por favor intenta otra vez")

    db.session.add(new_regimen)
    db.session.commit()
    res['msg'] = 'success'
    return res

def get_text_regimen(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)
    requirements = ['regimen_name']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
    mgr_id = request.authorization.username
    if mgr_id is None:
        abort(401, "No hay identificacion para el gerente")
    manager = Manager.query.filter(Manager.id == mgr_id).first()
    if manager is None:
        abort(401, "La identificacion del gerente es incorecto")
    manager_org_id = manager.org_id
    if manager_org_id is None:
        abort(422, "Este gerente no esta en un organizacion, por favor intenta con otra gerente")
    regimen = TextRegimen.query.filter(TextRegimen.regimen_name == form_data['regimen_name']).filter(TextRegimen.org_id == manager_org_id).all()
    if (len(regimen) == 0):
        abort(422, "No hay un regimen con este nombre para este organizacion")
    elif(len(regimen) != 1):
        abort(422, "Hay mas de uno regimen con este nombre. Manda un mensaje al Speranza por favor")
    else:
        res['regimen'] = regimen[0]
        res['msg'] = "success"
    return res

def get_org_text_regimens(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    mgr_id = request.authorization.username
    if mgr_id is None:
        abort(401, "No hay identificacion para el gerente")
    manager = Manager.query.filter(Manager.id == mgr_id).first()
    if manager is None:
        abort(401, "La identificacion del gerente es incorecto")
    manager_org_id = manager.org_id
    if manager_org_id is None:
        abort(422, "Este gerente no esta en un organizacion, por favor intenta con otra gerente")

    regimens = TextRegimen.query.filter(TextRegimen.org_id == manager_org_id).all()
    serialized_regimens = []
    for regimen in regimens:
        serialized_regimens.append(regimen.serialize)
    res['regimens'] = serialized_regimens
    res['msg'] = "success"
    return res

def get_org_texts(request, debug=False):
    res = {'msg':'Sorry something went wrong'}
    mgr_id = request.authorization.username
    if mgr_id is None:
        abort(401, "No hay identificacion para el gerente")
    manager = Manager.query.filter(Manager.id == mgr_id).first()
    if manager is None:
        abort(401, "La identificacion del gerente es incorecto")
    manager_org_id = manager.org_id
    if manager_org_id is None:
        abort(422, "Este gerente no esta en un organizacion, por favor intenta con otra gerente")

    texts = Text.query.filter(Text.org_id == manager_org_id).all()
    ser_texts = []
    for text in texts:
        ser_texts.append(text.serialize)
    res['texts'] = ser_texts
    res['msg'] = "success"
    return res