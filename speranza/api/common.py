from flask import abort, g

from speranza.mod_addresses.models import Address
from speranza.mod_managers.models import Manager
from speranza import db

"""
Common functions used across the API.
TODO needs refactoring and more thorough verification/sanitization
"""

GUAT_COUNTRY_CODE = '502'
USA_COUNTRY_CODE = '1'


# returns False if invalid request, True otherwise
def verify_new_user(request):
    form_data = get_form_data(request)

    if 'firstname' not in form_data or 'lastname' not in form_data or 'phone_number' not in form_data \
            or 'contact_number' not in form_data:
        if 'firstname' not in form_data:
            abort(422, "missing firstname")
        if 'lastname' not in form_data:
            abort(422, "missing lastname")
        if 'phone_number' not in form_data:
            abort(422, "missing phone_number")
        if 'contact_number' not in form_data:
            abort(422, "missing contact_number")
    if len(form_data['firstname']) == 0 or len(form_data['lastname']) == 0:
        abort(422, "names are too short")


def verify_password(username, password_or_token):
    mgr = Manager.verify_auth_token(password_or_token)
    if not mgr:
        mgr = Manager.query.filter(Manager.id == username).first()
        if not mgr or not mgr.verify_password(password_or_token):
            return False
    g.manager = mgr
    return True


def sanitize_phone_number(number):
    if len(number) == 8:
        new_number = GUAT_COUNTRY_CODE + str(number)
    else:
        new_number = str(number)
    return int(new_number)


# returns Address if valid, otherwise raises an error
def add_address(request):
    form_data = get_form_data(request)

    user_addr = Address()
    if 'street_num' in form_data:
        user_addr.street_num = form_data['street_num']
    if 'street_name' in form_data:
        user_addr.street_name = form_data['street_name']
    if 'street_type' in form_data:
        user_addr.street_type = form_data['street_type']
    if 'city_name' in form_data:
        user_addr.city_name = form_data['city_name']
    if 'zipcode' in form_data:
        user_addr.zipcode = form_data['zipcode']
    if 'district' in form_data:
        user_addr.district = form_data['district']

    try:
        print 'attempting to add address'
        db.session.add(user_addr)
        db.session.flush()
    except Exception, e:
        print 'exception adding address ', str(e)
        db.session.rollback()
        # db.session.flush()
        raise ValueError(str(e))
    return user_addr


def get_form_data(request):
    """Returns the request's json"""
    if request.get_json() is None:
        return request.form
    return request.get_json()


def verify_form_data(args, form_data):
    """Returns whether all the expected fields exist in the form"""
    for arg in args:
        if arg not in form_data:
            return False

    return True
