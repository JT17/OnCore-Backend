'''Put helper functions in this file to be shared across the api'''

def get_form_data(request):
#print request.get_json()
	if request.get_json() == None:
		return request.form
	return request.get_json()

# TODO make this more robust
def sanitize_phone_number(number):
#	print 'pre-sanitized', number
#	print len(number)
	new_number = ''
	if len(number) == 8:
		new_number = GUAT_COUNTRY_CODE + str(number)
	else:
		new_number = str(number)
#	print 'post-sanitized', new_number
	return int(new_number)
