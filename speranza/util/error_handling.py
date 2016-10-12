"""All of the error handling (including logging and alerts) for the api"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from speranza.util.logger import logger
from slack_poster import post_alert_to_slack


# error handling for all exceptions ex
def handle_error(ex):
    print "handle_error called"
    message = {
        'status': ex.code,
        'val': ex.description
    }

    # kinda hacky but i want to catch all 5xx errors as server errors
    # to get first digit cast int to string then index, then to compare to 5 cast back to int lol
    # if int(str(ex.code)[0]) == 5:
    #     logger.error(ex.description)
    #     post_alert_to_slack(ex.description)
    # else:
    #     logger.debug(ex.description)

    response = jsonify(message)
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response
