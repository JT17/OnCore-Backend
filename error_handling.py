'''All of the error handling (including logging and alerts) for the api'''

from werkzeug.exceptions import HTTPException
from flask import jsonify
import logging
from slackclient import SlackClient

#global definitions
ERR_LOG = './application/logs/speranza_error.log'
DEBUG_LOG = './application/logs/speranza_debug.log'
SLACK_TOKEN = 'xoxp-23808070245-23809034931-59911397713-e9163071cb'

#error handling for all exceptions ex
def handle_error(ex):
	message = {
			'status':ex.code,
			'val':ex.description
	}
	
	#kinda hacky but i want to catch all 5xx errors as server errors
	#to get first digit cast int to string then index, then to compare to 5 cast back to int lol
	if(int(str(ex.code)[0]) == 5):
		logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename= ERR_LOG, level=logging.DEBUG);
		logging.error(ex.description)
		post_alert_to_slack(ex.description)
	else:
		logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename= DEBUG_LOG , level=logging.DEBUG);
		logging.debug(ex.description)

	response = jsonify(message);
	response.status_code = (ex.code
				if isinstance(ex, HTTPException)
				else 500)
	return response

def post_alert_to_slack(message):
	slack_client = SlackClient(SLACK_TOKEN)
	slack_post =  slack_client.api_call(
			"chat.postMessage",
			channel='#alerts',
			text=message,
			username='error_bot',
			icon_emoji=':sob:'
			)

	if (slack_post['ok'] is not True):
		logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename= ERR_LOG, level=logging.DEBUG);
		logging.error('SLACK FAILED WITH: ' + slack_post['error'])
		

