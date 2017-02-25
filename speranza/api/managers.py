# coding=utf-8
from flask import abort, g

from speranza.models import Manager, Organization
from speranza.api.common import get_form_data, sanitize_phone_number
from speranza.api.verification import verify_form_data, verify_new_user
from speranza.util.mixpanel_logging import mp
from speranza.application import db
from speranza.util import email_messaging

REQUEST_LINK = "http://www.example.com/test2"


def verify_manager_access(patient, auth):
    manager = Manager.query.filter(Manager.id == int(auth.username)).first()
    return patient.grant_access(manager.org_id)


def verify_password(username, password_or_token):
    mgr = Manager.verify_auth_token(password_or_token)
    if not mgr:
        mgr = Manager.query.filter(Manager.id == username).first()
        if not mgr or not mgr.verify_password(password_or_token):
            return False
    return True

def login_manager(request, debug=False):
    res={'msg':'Something has gone wrong'}
    form_data = get_form_data(request, debug)
    requirements = ['username', 'password']
    if not verify_form_data(requirements, form_data):
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
    not_liar = verify_password(form_data['username'], form_data['password'])
    if(not_liar == False):
        abort(401, "Contrasena incorrecta")
    else:
        manager = Manager.query.filter(Manager.username == form_data['username']).first()
        if(manager is not None):
            res['msg'] = 'success'
            res['manager_id']  = manager.id
        else:
            abort(422, "Hay una problema, intenta otra vez por favor")
        if(manager.org_id is None):
            res['org_exists'] = False
        else:
            res['org_exists'] = True
            res['org_id'] = manager.org_id
        res['pending'] = manager.pending_access
        return res

def add_manager(request, debug=False):
    res = {'msg': 'Something has gone wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['username','firstname', 'lastname', 'password', 'phone_number', 'email']
    if not verify_form_data(requirements, form_data):
        print "failed verification of data"
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
    if not verify_new_user(form_data):
        print "need more info"
        abort(422, "Necesita mas informacion, intenta otra vez por favor")
    username_exists = Manager.query.filter(Manager.username == form_data['username']).first()
    if(username_exists is not None):
        print "username exists"
        abort(422, "Nombre de usuario ya tomado, intenta otra vez por favor")
    phone_number = sanitize_phone_number(form_data['phone_number'])
    manager = Manager(form_data['firstname'], form_data['lastname'], form_data['username'],
                      phone_number, form_data['email'], form_data['password'])
    try:
        db.session.add(manager)
        db.session.commit()
        if not debug:
            mp.track(manager.id, "Manager added",
                     properties={'firstname': form_data['firstname'], 'lastname': form_data['lastname'], 'username':form_data['username']})
    except ValueError as err:
        db.session.flush()
        abort(500, str(err.args))

    res['msg'] = 'success'
    res['manager_id'] = manager.id
    return res

def edit_manager(request, debug=False):
    res = {'msg':'Something has gone wrong'}
    form_data = get_form_data(request, debug)

    user_id = request.authorization.username
    pwd = request.authorization.password
    if(verify_password(user_id, pwd) == False):
        abort(401, "La contrasena es incorecto, intentalo otra vez por favor")
    else:
        mgr = Manager.query.filter(Manager.id == user_id).first()
        if ('new_pwd' in form_data):
            mgr.update_password(form_data['new_pwd'])
        if('new_email' in form_data):
            mgr.email = form_data['new_email']
        db.session.commit()
    res['msg'] = 'success'
    return res

# sends out an email to all of the admins with a link
# TODO talk to deepak for specifics of email to be sent e.g. the url string
def ask_for_org_access(request, debug=False):
    res = {'msg': 'Sorry something went wrong'}
    form_data = get_form_data(request, debug)

    requirements = ['org_id']
    if not verify_form_data(form_data, requirements):
        abort(422, "Necesita mas informacion, intenta otra vez por favor")

    mgr_id = request.authorization.username
    if mgr_id is not None:
        mgr = Manager.query.filter(Manager.id == mgr_id).first()
        if mgr is None:
            abort(422, "La identificion del gerente es incorrecto")
        else:
            mgr.pending_access = True
            db.session.commit()
    else:
        abort(401, "No hay identificacion para el gerente")

    org = Organization.query.filter(Organization.id == form_data['org_id']).first()
    if org is None:
        abort(422, "No hay organizacion con este identificacion")

    request = REQUEST_LINK + "/mgr_id/" + str(mgr.id) + "/org/" + str(org.id) + "/name/" + mgr.firstname + "%20" + mgr.lastname
    msg_text = "Hola, \r\n Me llamo {0} {1} y quiero unirme al {2} organizacion. " \
               "Puede agregame al organizacion con este hipirenlace: {3}. \r\n Muchas Gracias, " \
               "\r\n {4}".format(mgr.firstname, mgr.lastname, org.org_name, request, mgr.firstname)

    subj = "Añada un gerente al orgnizacion {0}".decode("utf-8").format(org.org_name)

    admin_emails = [admin.email for admin in org.admins]

    if debug is False:
        res['msg'] = email_messaging.send_email(msg_text, admin_emails, subj)
    else:
        res['msg'] = email_messaging.send_email(msg_text, [], subj, debug=True)
    return res
