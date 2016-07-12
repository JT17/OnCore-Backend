from werkzeug.exceptions import HTTPException
from flask import jsonify
#error handling for all exceptions ex
def make_json_error(ex):
	response = jsonify(message =str(ex))
	response.status_code = (ex.code
				if isinstance(ex, HTTPException)
				else 500)
	return response
