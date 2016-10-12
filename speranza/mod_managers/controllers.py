from flask import Blueprint, request, abort, jsonify

from speranza.application import auth
import speranza.api.managers

mod_managers = Blueprint('managers', __name__)


@mod_managers.route('/api/add_manager', methods=['GET', 'POST'])
def add_manager():
    res = speranza.api.managers.add_manager(request)
    if res['msg'] == 'success':
        return jsonify(status='200', value=res['msg'], manager_id=res['manager_id'])
    else:
        abort(500, res['msg'])


@mod_managers.route('/api/edit_manager', methods=['GET', 'POST'])
@auth.login_required
def edit_manager():
    pass
    # TODO
    # res = speranza.api.managers.edit_manager(request)
    # if res['msg'] == "success":
    #     return jsonify(status="200", value=res['msg'], manager_id=res['manager_id'],
    #                    manager_contact_number=res['manager_contact_number'])
    # else:
    #     abort(500)


@mod_managers.route('/api/delete_manager', methods=['GET', 'POST'])
@auth.login_required
def delete_manager():
    pass
    # TODO
    # res = speranza.api.managers.delete_manager(request)
    # if res['msg'] == "success":
    #     return jsonify(status="200", value=res['msg'], manager_id=res['manager_id'],
    #                    manager_contact_number=res['manager_contact_number'])
    # else:
    #     abort(500)



@mod_managers.route('/api/find_manager', methods=['GET', 'POST'])
@auth.login_required
def find_manager():
    pass
    # TODO
    # res = speranza.api.managers.find_manager(request)
    # if res['msg'] == "success":
    #     return jsonify(status="200", value=res['msg'], manager_id=res['managers_id'],
    #                    manager_contact_number=res['manager_contact_number'])
    # else:
    #     abort(500)
