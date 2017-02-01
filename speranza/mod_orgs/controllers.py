from flask import Blueprint, request, abort, jsonify

from speranza.application import auth
import speranza.api.organizations

mod_orgs = Blueprint('organizations', __name__)


@mod_orgs.route('/api/get_organizations', methods=['GET', 'POST'])
def get_organizations():
    res = speranza.api.organizations.get_organizations(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], orgs=res['orgs'])
    else:
        abort(500, res['msg'])

@mod_orgs.route('/api/add_organization', methods=['GET', 'POST'])
def add_organization():
    res = speranza.api.organizations.add_organization(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], org=res['org'], org_id=res['org_id'])
    else:
        abort(500, res['msg'])

@mod_orgs.route('/api/get_org_appt_types', methods=['GET'])
@auth.login_required
def get_org_appt_types():
    res = speranza.api.organizations.get_org_appt_types(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], appt_types = res['appt_types'])
    else:
        abort(500, res['msg'])