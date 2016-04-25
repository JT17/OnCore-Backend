from application.models import *
from flask import Flask, request, redirect, jsonify, g

def add_appt(request):
	print "add_appt2"
	if 'user_id' in request.form and 'date' in request.form:
		new_appt = Appointment(request.form['user_id'], request.form['date']);
		try:
			db.session.add(new_appt);
			db.session.commit();
		except:
			db.session.rollback()
			#db.session.flush();
			print "wrong"
			return str("Could not create new appt :( something went wrong");
		print "success"
		return str("Successfully added a new appt!");
	else:
		print "wrong2"
		return str("Could not create new appt :( missing post values");


	
def add_address(request):
	firstname = request.form['firstname'];
	if 'firstname' not in request.form or 'lastname' not in request.form or 'phone_number' not in request.form \
		or 'contact_number' not in request.form: 
		return str("Could not create new user, missing form values :(");
	
	user_addr = Address();
	if request.form.has_key('street_num'):
		user_addr.street_num = request.form['street_num'];
	if request.form.has_key('street_name'):
		user_addr.street_name = request.form['street_name'];
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
		db.session.rollback()
		# db.session.flush();
		raise ValueError("Could not create address for user something went wrong :(");
	return user_addr;
	
def add_patient(request):
	try:
		patient_addr = add_address(request);
	except ValueError as err:
		return err.args
	if request.form.has_key('manager_id'):
		manager = Manager.query.filter(Manager.id == request.form['manager_id'])
		if manager == None:
			return str("Sorry incorrect manager id, please resend form")
		else:
			patient = Patient(request.form['firstname'], request.form['lastname'], request.form['phone_number'],
					request.form['contact_number'], patient_addr.id, manager.id);
			try:
				db.session.add(patient);
				db.session.commit();
			except:
				db.session.flush();
				raise ValueError("Could not create patient, something went wrong sorry");
	else:
		return str("Need a manager_id");
	return str("Successfully added patient");


def add_manager(request):
	try:
		addr = add_address(request);
	except ValueError as err:
		return err.args;
	
	if request.form.has_key('password'):
		manager = Manager(request.form['firstname'], request.form['lastname'],
			       	request.form['phone_number'], request.form['contact_number'], 
				addr.id, request.form['password']);
		try:
			db.session.add(manager);
			db.session.commit();
		except ValueError:
			db.session.flush();
			raise ValueError("Could not create manager, something went wrong sorry");
	return str("Successfully created manager");

def verify_password(username_or_token, password):
	user = User.verify_auth_token(username_or_token)
	if not user:
		mgr = Manager.query.filter_by(id = username_or_token).first();
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

