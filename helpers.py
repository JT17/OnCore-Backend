from werkzeug.exceptions import HTTPException
from flask import jsonify
import logging
ERR_LOG = './application/logs/speranza_error.log'
DEBUG_LOG = './application/logs/speranza_debug.log'
#error handling for all exceptions ex
def handle_error(ex):
	message = {
			'status':ex.code,
			'val':ex.description
	}

	if(ex.code == 500):
		logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename= ERR_LOG, level=logging.DEBUG);
		logging.error(ex.description)
	else:
		logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename= DEBUG_LOG , level=logging.DEBUG);
		logging.debug(ex.description)

	response = jsonify(message);
	response.status_code = (ex.code
				if isinstance(ex, HTTPException)
				else 500)
	return response

def get_form_data(request):
	print request.get_json()
	if request.get_json() == None:
		return request.form
	return request.get_json()
