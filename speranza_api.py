from application.models import *
from flask import Flask, request, redirect, jsonify, g
from dateutil import parser
import requests

# Download the twilio-python library from http://twilio.com/docs/libraries
 
# Find these values at https://twilio.com/user/account
# account_sid = "AC67374f743c7b1e1625827c13822f5f2b"
# auth_token = "b1a10dd37717ed58a50664a27e9a71c5"
# client = TwilioRestClient(account_sid, auth_token)

ADD_PATIENT_MESSAGE = "jointestgroup"
FRONTLINESMS_API_KEY = "309fefe6-e619-4766-a4a2-53f0891fde23"
FRONTLINESMS_WEBHOOK = "https://cloud.frontlinesms.com/api/1/webhook"

def add_appt(request):
	if 'user_id' in request.form and 'date' in request.form:
		import datetime

		timestamp = parser.parse(str(request.form['date']))
		new_appt = Appointment(request.form['user_id'], timestamp);

		#error check that manager making appt is the patient's manager
		patient = Patient.query.filter(Patient.id == request.form['user_id']).first();
		auth = request.authorization
		if patient.manager_id != int(auth.username):
			return str("Wrong manager");
		try:
			db.session.add(new_appt);
			db.session.commit();
		except Exception, e:
			print str(e);
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

'''
You can now access the endpoint https://cloud.frontlinesms.com/api/1/webhook

This endpoint accepts POST Requests with JSON payloads

The JSON payload should be in the following format:

{"apiKey":"Your API Key", "payload":{"message":"Send a message from a remote app", 
"recipients":[{ "type":"groupName", "value":"friends" }, { "type":"smartgroupName", "value":"humans" }, 
{ "type":"contactName", "value":"bobby" }, { "type":"mobile", "value":"+1234567890" }, { "type":"mobile", "value":"+1234567891" }]}}

API_KEY = "309fefe6-e619-4766-a4a2-53f0891fde23"
'''
	
def add_patient(request):
	try:
		patient_addr = add_address(request);
	except ValueError as err:
		return err.args
	auth = request.authentication
	if auth.username:
		manager = Manager.query.filter(Manager.id == int(auth.username))
		if manager == None:
			return str("Sorry incorrect manager id, please resend form")
		else:
			try:
				patient = Patient(request.form['firstname'], request.form['lastname'], request.form['phone_number'], 
					request.form['contact_number'], patient_addr.id, auth.username);
				
				# message = client.messages.create(to=request.form['phone_number'], from_=request.form['phone_number'],body=add_patient_message)
				message = "Thanks for joining Speranza Health"

				r = requests.post(FRONTLINESMS_WEBHOOK, json={"apiKey": FRONTLINESMS_API_KEY, 
					"payload":{"message": message, "recipients":[{"type": "mobile", "value": request.form['phone_number']}]}});

				db.session.add(patient);
				db.session.commit();
			except:
				db.session.flush();
				raise ValueError("Could not create patient, something went wrong sorry");
			else:
				return str("Need a manager");
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
		return str("Successfully created manager with id " + str(manager.id));
	else:
		return str("No password entered");

def get_managers(request):
	managers = Manager.query.all();
	return managers;

def get_patients(request):
	pts = Patient.query.all();
	return pts;

def verify_password(username, password_or_token):
	print password_or_token 
	mgr = Manager.verify_auth_token(password_or_token)
	if not mgr:
		mgr = Manager.query.filter_by(id = username).first();
		print "calling mgr.verify_password:"
		print mgr.verify_password(password_or_token);
		if not mgr or not mgr.verify_password(password_or_token):
			return False;
	g.manager= mgr 
	return True;

def get_user_appts(request):
	import json
	if 'user_id' not in request.form:
		return str("Could not get appts, missing form values :(");
	try:
		auth = request.authorization
		user = Patient.query.filter(Patient.id == request.form['user_id']).first()
		if user.manager_id != int(auth.username):
			return str("Invalid manager id");	
		appts = Appointment.query.filter(Appointment.user_id == request.form['user_id'])
		all_appts = Appointment.query.all()
		print len(all_appts)
		for val in all_appts:
			print val.user_id
		return jsonify(json_list=[i.serialize() for i in appts.all()])
	except ValueError:
		return str("Couldn't fetch your appointments something went wrong :(");

