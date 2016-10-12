from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from speranza.util.logger import h1, h2

# Define the WSGI application object
application = Flask(__name__)

# Configurations
application.config.from_object('config')
application.debug = False
application.secret_key = '3treelandscaping'

# Application logging
application.logger.addHandler(h1)
application.logger.addHandler(h2)

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(application)

# TODO using simple HTTP auth at the moment. Should use HTTPS for everything.
auth = HTTPBasicAuth()


@application.errorhandler(404)
def not_found():
    return render_template('404.html'), 404


@application.route("/", methods=['GET', 'POST'])
def index():
    print "get /"
    return render_template('index.html', appts=[], patients=[])


@application.before_request
def log_entry():
    application.logger.debug("Handling request")


@application.after_request
def log_result(response):
    application.logger.debug("Response with code %s and data %s" % (response.status, str(response.get_data())))
    return response
