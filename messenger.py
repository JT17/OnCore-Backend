import plivo

auth_id = "MAY2ZKYMZHNJZMN2Q4NT"
auth_token = "YzFjM2E5ODFhNzM3YzIyMmI3NmU0N2FhZmM5ODgw"
src_phone = '+18057424820'

p = plivo.RestAPI(auth_id, auth_token)

def send_message(message, phone_number, DEBUG):
	if DEBUG == True:
		return;
	params = {
	    'src': src_phone, # Sender's phone number with country code
	    'dst' : phone_number, # Receiver's phone Number with country code
	    'text' : message, # Your SMS Text Message - English
	#    'url' : "http://example.com/report/", # The URL to which with the status of the message is sent
	    'method' : 'POST' # The method used to call the url
	}

	response = p.send_message(params)

	# Prints the complete response
	print params
	print str(response)
	return response

	# r = requests.post(FRONTLINESMS_WEBHOOK, json={"apiKey": FRONTLINESMS_API_KEY, 
	# 	"payload":{"message": message, "recipients":[{"type": "mobile", "value": '+'+str(phone_number)}]}});
	# return r;

	
