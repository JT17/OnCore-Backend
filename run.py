from werkzeug.exceptions import default_exceptions

from speranza import application
from speranza.util import error_handling

if __name__ == '__main__':
    """Run the Speranza Health backend"""
    # Add custom error handling for all exceptions
    print "started running"
    # for code in default_exceptions.iterkeys():
    #     application.error_handler_spec[None][code] = error_handling.handle_error

    print "try to run app"
    try:
        application.run(host='0.0.0.0', debug=True)
    except KeyboardInterrupt:
        application.stop()
