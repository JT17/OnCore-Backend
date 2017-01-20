from speranza.mod_appointments.controllers import mod_appointments
from speranza.mod_auth.controllers import mod_auth
from speranza.mod_managers.controllers import mod_managers
from speranza.mod_patients.controllers import mod_patients
from speranza.mod_orgs.controllers import  mod_orgs
from speranza.application import application
from speranza.application import db


# Register blueprints
application.register_blueprint(mod_appointments)
application.register_blueprint(mod_auth)
application.register_blueprint(mod_managers)
application.register_blueprint(mod_patients)
application.register_blueprint(mod_orgs)
db.create_all()
