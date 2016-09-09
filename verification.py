from application.models import *
from flask import abort
def verify_manager_access(patient_id, auth):
	patient = Patient.query.filter(Patient.id == patient_id).first()
	manager = Manager.query.filter(Manager.id == int(auth.username)).first()
	return patient.grant_access(manager.org_id)

def verify_form_data(args, form_data):
	for arg in args:
		if arg not in form_data:
			return False;

	return True;

def verify_patient_exists(patient_id):
	return len(Patient.query.filter(Patient.id == patient_id).all()) == 1

def verify_new_user(form_data):
	if len(form_data['firstname']) == 0 or len(form_data['lastname']) == 0:
		abort(422, "names are too short")
#	if pn.isdigit() == False or cn.isdigit() == False or (len(pn) == 0) or (len(cn) == 0):
#		print "phone number isn't digit"
#		return False;

def verify_password(username, password_or_token):
	mgr = Manager.verify_auth_token(password_or_token)
	if not mgr:
		mgr = Manager.query.filter(Manager.id == username).first();
		if not mgr or not mgr.verify_password(password_or_token):
			return False;
	g.manager= mgr 
	return True;
