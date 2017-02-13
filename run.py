import os
from werkzeug.exceptions import default_exceptions

from speranza import application
from speranza.util import error_handling

if __name__ == '__main__':
    """Run the Speranza Health backend"""
    # Add custom error handling for all exceptions
    print "Running the Speranza Health backend..."
    # for code in default_exceptions.iterkeys():
    #     application.error_handler_spec[None][code] = error_handling.handle_error

    try:
	application.run(host= '192.168.1.72', port=9000, debug=False)
	#application.run(host="0.0.0.0", port=os.environ["PORT"], debug=False)
    except KeyboardInterrupt:
        application.stop()
