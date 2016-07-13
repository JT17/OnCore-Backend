from werkzeug.exceptions import HTTPException
from flask import jsonify
#error handling for all exceptions ex
def make_json_error(ex):
	print "HI!"
	message = {
			'status':ex.code,
			'val':ex.description
	}
	print message
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
