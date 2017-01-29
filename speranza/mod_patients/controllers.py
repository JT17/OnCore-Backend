from flask import Blueprint, redirect, request, abort, jsonify

from speranza.application import auth
import speranza.api.patients

mod_patients = Blueprint('patients', __name__)


@mod_patients.route('/api/add_patient', methods=['GET', 'POST'])
@auth.login_required
def add_patient():
    res = speranza.api.patients.add_patient(request)
    if res['msg'] == "success":
        return jsonify(status="200", value=res['msg'], patient_id=res['patient_id'], patient_name = res['patient_name'],
                       last_appt_details=res['last_appt_details'], phone_number=res['patient_phone_number'])
    else:
        abort(500)


@mod_patients.route('/api/edit_patient', methods=['GET', 'POST'])
@auth.login_required
def edit_patient():
    res = speranza.api.patients.edit_patient(request)
    if res['msg'] == "success":
        return jsonify(status="200", value=res['msg'], patient_id=res['patient_id'],
                       patient_contact_number=res['patient_contact_number'])
    else:
        abort(500)


@mod_patients.route('/api/delete_patient', methods=['GET', 'POST'])
@auth.login_required
def delete_patient():
    res = speranza.api.patients.delete_patient(request)
    if res['msg'] == "success":
        return jsonify(status="200", value=res['msg'], patient_id=res['patient_id'],
                       patient_contact_number=res['patient_contact_number'])
    else:
        abort(500)


@mod_patients.route('/api/find_patient', methods=['GET', 'POST'])
@auth.login_required
def find_patient():
    res = speranza.api.patients.find_patient(request)
    if res['msg'] == "success":
        print res['patients']
        return jsonify(status="200", value=res['msg'], patients = res['patients'])
    else:
        abort(500)
