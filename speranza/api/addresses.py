from flask import abort

from speranza.api.common import get_form_data
from speranza.api.patients import Patient
from speranza.mod_addresses.models import Address
from speranza import db


def get_all_addresses():
    """Returns all addresses (god view)"""
    return Address.query.all()


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
