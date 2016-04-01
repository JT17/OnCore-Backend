from database import db_session
from models import *
from flask import Flask, request, redirect, jsonify
from start_server import app

def add_appt(request):
	if 'user_id' in request.form and 'date' in request.form:
		new_appt = Appointment(request.form['user_id'], request.form['date']);
		try:
			db_session.add(new_appt);
			db_session.commit();
		except:
			db_session.flush();
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
		user_addr.distrcit = request.form['district'];
	
	try:
		db_session.add(user_addr);
		db_session.flush();
	except:
		db_session.flush();
		return str("Could not create address for user something went wrong :(");

	new_user = User(request.form['firstname'], request.form['lastname'], request.form['phone_number'], request.form['contact_number'], user_addr.id);
	try:
		db_session.add(new_user);
		db_session.commit();
	except:
		db_session.flush();
		return str("Could not create user something went wrong sorry :(");
	return str("Successfully created user!");

def get_user_appts(request):
	import json
	if 'user_id' not in request.form:
		return str("Could not get appts, missing form values :(");
#	try:
	appts = Appointment.query.filter(Appointment.user_id == request.form['user_id'])
	print appts[0]
	return jsonify(json_list=[i.serialize() for i in appts.all()])
#	except:
#		return str("Couldn't fetch your appointments something went wrong :(");
	return str(resp);

