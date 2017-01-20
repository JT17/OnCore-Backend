from flask import Blueprint, request, abort, jsonify

from speranza.application import auth
import speranza.api.organizations

mod_orgs = Blueprint('organizations', __name__)


@mod_orgs.route('/api/get_organizations', methods=['GET', 'POST'])
def get_organizations():
    print "what the fuck"
    res = speranza.api.organizations.get_organizations(request)
    print res
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], orgs=res['orgs'])
    else:
        abort(500, res['msg'])