'''Put helper functions in this file to be shared across the api'''

def get_form_data(request):
#print request.get_json()
	if request.get_json() == None:
		return request.form
	return request.get_json()

def verify_form_data(args, form_data):
	for arg in args:
		if arg not in form_data:
			return False;

	return True;
