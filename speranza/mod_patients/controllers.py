from flask import Blueprint, redirect, request, abort, jsonify

from speranza.application import auth
import speranza.api.patients


mod_patients = Blueprint('patients', __name__)


# God view
@mod_patients.route('/get_all_patients', methods=['GET', 'POST'])
def get_patients():
    pts = speranza.api.patients.get_patients()
    for val in pts:
        print val.firstname, val.id, val.manager_id, val.phone_number, val.contact_number
    return redirect('/')


@mod_patients.route('/api/add_patient', methods=['GET', 'POST'])
@auth.login_required
def add_patient():
    res = speranza.api.patients.add_patient(request)
    if res['msg'] == "success":
        return jsonify(status="200", value=res['msg'], patient_id=res['patient_id'],
                       patient_contact_number=res['patient_contact_number'])
    else:
        abort(500)
