from flask import abort

from speranza.api.common import get_form_data
from speranza.models import Address, Patient
from speranza.application import db


def get_all_addresses():
    """Returns all addresses (god view)"""
    return Address.query.all()


# returns Address if valid, otherwise raises an error
def add_address(request, debug=False):
    form_data = get_form_data(request, debug)
    user_addr = Address()

    # TODO list comprehension util
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
        db.session.add(user_addr)
        db.session.commit()
    except Exception, e:
        print 'exception adding address ', str(e)
        db.session.rollback()
        # db.session.flush();
        raise ValueError(str(e))
    return user_addr


def edit_patient_address(request):
    # res = {'msg': 'something has gone wrong'}
    form_data = get_form_data(request)

    if 'user_id' not in form_data:
        abort(422, "Could not edit patient, missing user_id in form")
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
            db.session.rollback()
            print e
            abort(500, "something went wrong")
