from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

from speranza.mod_appointments.controllers import mod_appointments
from speranza.mod_auth.controllers import mod_auth
from speranza.mod_managers.controllers import mod_managers
from speranza.mod_patients.controllers import mod_patients

# Define the WSGI application object
application = Flask(__name__)

# Configurations
application.config.from_object('config')
application.debug = True
application.secret_key = '3treelandscaping'

# Register blueprints
application.register_blueprint(mod_appointments)
application.register_blueprint(mod_auth)
application.register_blueprint(mod_managers)
application.register_blueprint(mod_patients)

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(application)
db.create_all()

# TODO using simple HTTP auth at the moment. Should use HTTPS for everything.
auth = HTTPBasicAuth()


@application.errorhandler(404)
def not_found():
    return render_template('404.html'), 404


@application.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html', appts=[], patients=[])
