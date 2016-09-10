from flask import Blueprint, request, abort, jsonify

import speranza.api.appointments
from speranza import auth

mod_appointments = Blueprint('appointments', __name__)


# God view
@mod_appointments.route('/get_all_appts', methods=['GET', 'POST'])
def get_all_appts():
    res = speranza.api.appointments.get_all_appts()
    if res['msg'] == 'success':
        jsonify(status='200', value=str(res['msg']), appts=res['appts'])
    else:
        abort(500, res['msg'])


@mod_appointments.route('/api/get_patient_appts', methods=['GET', 'POST'])
@auth.login_required
def get_patient_appts():
    appts = speranza.api.appointments.get_patient_appts(request)
    ser_appts = []
    for val in appts:
        ser_appt = {'user_id': val.user_id, 'date': val.date, 'appt_type': val.appt_type, 'checkin': val.checkin}
        ser_appts.append(ser_appt)
    return jsonify(appts=ser_appts)


@mod_appointments.route('/api/get_manager_appts', methods=['GET', 'POST'])
@auth.login_required
def get_manager_appts():
    appts = speranza.api.appointments.get_manager_appts(request)
    ser_appts = []
    for val in appts:
        ser_appt = {'user_id': val.user_id, 'date': val.date, 'appt_type': val.appt_type, 'checkin': val.checkin}
        ser_appts.append(ser_appt)
    return jsonify(appts=ser_appts)


# requires user_id, date, appt_type in request form
@mod_appointments.route('/api/add_appt', methods=['GET', 'POST'])
@auth.login_required
def add_appt():
    res = speranza.api.appointments.add_appt(request)
    if res['msg'] == "success":
        return jsonify(status="200", value=res['msg'])
    else:
        abort(500, res['msg'])


# requires user_id, old_date (date of first appt) and then new_date || appt_type
# so can change either new_date and or appt_type
# if you have neither it'll work but nothing happens
@mod_appointments.route('/api/edit_appt', methods=['GET', 'POST'])
@auth.login_required
def edit_appt():
    res = speranza.api.appointments.edit_appt(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=str(res['msg']))
    else:
        abort(500, res['msg'])


# requires user_id and date
@mod_appointments.route('/api/delete_appt', methods=['GET', 'POST'])
@auth.login_required
def delete_appt():
    res = delete_appt(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=str(res['msg']))
    else:
        abort(500, res['msg'])


# requires user_id, date
@mod_appointments.route('/api/checkin', methods=['GET', 'POST'])
@auth.login_required
def checkin_appt():
    res = speranza.api.appointments.checkin_out(request, checkin=True)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'])
    else:
        abort(500, res['msg'])


# requires user_id, date
@mod_appointments.route('/api/checkout', methods=['GET', 'POST'])
@auth.login_required
def checkout_appt():
    res = speranza.api.appointments.checkin_out(request, checkin=False)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'])
    else:
        abort(500, res['msg'])
