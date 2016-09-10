"""Sends messages to plivo"""

import plivo

AUTH_ID = "MAY2ZKYMZHNJZMN2Q4NT"
AUTH_TOKEN = "YzFjM2E5ODFhNzM3YzIyMmI3NmU0N2FhZmM5ODgw"
SRC_PHONE = '+18057424820'

p = plivo.RestAPI(AUTH_ID, AUTH_TOKEN)


def send_message(message, phone_number, debug=False):
    """Send a message through plivo"""
    params = {
        'src': AUTH_ID,  # Sender's phone number with country code
        'dst': phone_number,  # Receiver's phone Number with country code
        'text': message,  # Your SMS Text Message - English
        #    'url' : "http://example.com/report/", # The URL to which with the status of the message is sent
        'method': 'POST'  # The method used to call the url
    }

    if debug:
        return params
    else:
        return p.send_message(params)
