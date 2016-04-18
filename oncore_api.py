from application.models import *
from flask import Flask, request, redirect, jsonify, g

def add_appt(request):
	if 'user_id' in request.form and 'date' in request.form:
		new_appt = Appointment(request.form['user_id'], request.form['date']);
		try:
			db.session.add(new_appt);
			db.session.commit();
		except:
			db.session.flush();
			return str("Could not create new appt :( something went wrong");
		return str("Successfully added a new appt!");
	else:
		return str("Could not create new appt :( missing post values");


	
def add_user(request):
	firstname = request.json.get('firstname');
	if firstname is None:
		return str("firstname is none as caught by the json get");
	if 'firstname' not in request.form or 'lastname' not in request.form or 'phone_number' not in request.form \
		or 'contact_number' not in request.form: 
		return str("Could not create new user, missing form values :(");
	
	user_addr = Address();
	if request.form.has_key('street_num'):
		user_addr.street_num = request.form['street_num'];
	if request.form.has_key('street_name'):
		user_addr.street_num = request.form['street_name'];
	if request.form.has_key('street_type'):
		user_addr.street_type = request.form['street_type'];
	if request.form.has_key('city_name'):
		user_addr.city_name = request.form['city_name'];
	if request.form.has_key('zipcode'):
		user_addr.zipcode = request.form['zipcode'];
	if request.form.has_key('district'):
		user_addr.district = request.form['district'];
	
	try:
		db.session.add(user_addr);
		db.session.flush();
	except:
		db.session.flush();
		raise ValueError("Could not create address for user something went wrong :(");

	new_user = User(request.form['firstname'], request.form['lastname'], request.form['phone_number'], request.form['contact_number'], user_addr.id);
	try:
		db.session.add(new_user);
		db.session.commit();
	except:
		db.session.flush();
		raise ValueError("Could not create user something went wrong sorry :(");
	return 0;
	
def add_patient(request):
	try:
		add_user(request);
	except ValueError as err:
		return err.args
	
	if request.form.has_key('manager_id'):
		manager = Manager.query.filter(Manager.id == request.form['manager_id'])
		if manager == None:
			return str("Sorry incorrect manager id, please resend form")
		else:
			patient = Patient(request.form['manager_id']);
			try:
				db.session.add(patient);
				db.session.commit();
			except:
				db.session.flush();
				raise ValueError("Could not create patient, something went wrong sorry");
	return str("Successfully added patient");


def add_manager(request):
	try:
		add_user(request);
	except ValueError as err:
		return err.args;
	
	if request.form.has_key('password'):
		manager = Manager(request.form['password']);
		try:
			db.session.add(manager);
			db.session.commit();
		except:
			db.session.flush();
			raise ValueError("Could not create manager, something went wrong sorry");
	return str("Successfully created manager");

def verify_password(self, username_or_token, password):
	user = User.verify_auth_token(username_or_token)
	if not user:
		mgr = Manager.query.filter_by(username = username_or_token).first();
		if not user or not mgr.verify_password(password, self.password):
			return False;
	g.user = user
	return True;

def get_user_appts(request):
	import json
	if 'user_id' not in request.form:
		return str("Could not get appts, missing form values :(");
#	try:
	appts = Appointment.query.filter(Appointment.user_id == request.form['user_id'])
	return jsonify(json_list=[i.serialize() for i in appts.all()])
#	except:
#		return str("Couldn't fetch your appointments something went wrong :(");
	return str(resp);

