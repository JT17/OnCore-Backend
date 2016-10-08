from flask import Blueprint, request, abort, jsonify

from speranza.application import auth
import speranza.api.managers
from speranza.util.logger import logger

mod_managers = Blueprint('managers', __name__)


# God view
@mod_managers.route('/get_all_managers', methods=['GET', 'POST'])
def get_all_managers():
    managers = speranza.api.managers.get_all_managers()
    for val in managers:
        print val.firstname, val.id, val.manager_id, val.phone_number, val.contact_number


@mod_managers.route('/api/add_manager', methods=['GET', 'POST'])
def add_manager():
    res = speranza.api.managers.add_manager(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], manager_id=res['mgr_id'])
    else:
        abort(500, res['msg'])
