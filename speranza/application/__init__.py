from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
application = Flask(__name__)

# Configurations
application.config.from_object('config')
application.debug = False
application.secret_key = '3treelandscaping'

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(application)

# TODO using simple HTTP auth at the moment. Should use HTTPS for everything.
auth = HTTPBasicAuth()


@application.errorhandler(404)
def not_found():
    return render_template('404.html'), 404


@application.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html', appts=[], patients=[])
