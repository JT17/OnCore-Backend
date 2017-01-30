from flask import Blueprint, request, abort, jsonify

from speranza.application import auth
import speranza.api.organizations

mod_texts = Blueprint('texts', __name__)


@mod_texts.route('/api/add_text_regimen', methods=['GET','POST'])
@auth.login_required
def add_text_regimen():
    res = speranza.api.organizations.add_text_regimen(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'])
    else:
        abort(500, res['msg'])

@mod_texts.route('/api/get_patient_text_regimen', methods=['GET', 'POST'])
@auth.login_required
def get_patient_text_regimen():
    res = speranza.api.organizations.get_text_regimen(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], text_regimen=res['text_regimen'])
    else:
        abort(500, res['msg'])

@mod_texts.route('/api/get_org_text_regimens', methods=['GET','POST'])
@auth.login_required
def get_org_text_regimens():
    res = speranza.api.organizations.get_org_text_regimens(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], text_regimens = res['regimens'])
    else:
        abort(500, res['msg'])

@mod_texts.route('/api/get_org_texts', methods=['GET', 'POST'])
@auth.login_required
def get_org_texts():
    res = speranza.api.organizations.get_org_texts(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], texts = res['texts'])
    else:
        abort(500, res['msg'])