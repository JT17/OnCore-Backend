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
	res = {'msg':'Sorry something went wrong'}
	if 'user_id' in request.form and 'date' in request.form and 'appt_type' in request.form:
		#error check that manager making appt is the patient's manager
		patient = Patient.query.filter(Patient.id == request.form['user_id']).first();
		if patient is None:
			res['msg'] = 'Bad patient id'
			res['bad_id'] = request.form['user_id']
			return res 
		auth = request.authorization
		if patient.manager_id != int(auth.username):
			res['msg'] = 'Wrong manager'
			return res; 
		try:
			import datetime
			print float(request.form['date'])
			timestamp = datetime.datetime.utcfromtimestamp(float(request.form['date']));
			print timestamp
			exists = Appointment.query.filter(Appointment.user_id == request.form['user_id']).filter(Appointment.date == timestamp);
			if exists.first() is not None:
				res['msg'] = "Appt for this patient already exists at this date";
				return res;
			new_appt = Appointment(request.form['user_id'], timestamp, request.form['appt_type']);
			db.session.add(new_appt);
			db.session.commit();
			res['msg'] = 'success'
		except Exception, e:
			db.session.rollback()
			res['msg'] = str(e)
			#db.session.flush();
			return res;
		return res;
	else:
		res['msg'] = "Could not create new appt missing post values"
		return res;

def checkin_out(request, checkin = True):
	res = {'msg':'Sorry something went wrong'}
	if 'user_id' in request.form and 'date' in request.form:
		patient = Patient.query.filter(Patient.id == request.form['user_id']).first();
		if patient is None:
			res['msg'] = 'Bad patient id'
			return res;
		auth = request.authorization
		if patient.manager_id != int(auth.username):
			res['msg'] = 'Wrong manager'
			return res;
		try:
			import datetime
			timestamp = datetime.datetime.utcfromtimestamp(float(request.form['date']))
			appt = Appointment.query.filter(Appointment.user_id == request.form['user_id']).filter(Appointment.date == timestamp).first()
			if appt is None:
				res['msg'] = 'Cannot checkin for nonexistent appt, please try again';
				return res;
			if checkin == True:
				if appt.checkin == True:
					res['msg'] = 'Already checked in'
					return res;
				appt.checkin = True;
			else:
				if appt.checkout == True:
					res['msg'] = 'Already checked out'
					return res;
				appt.checkout = True;
			db.session.commit();
			res['msg'] = 'success'
			return res;
		except Exception, e:
			db.session.rollback();
			res['msg'] = str(e);
			return res;
	else:
		res['msg'] = 'Missing post values';
		return res;	

def add_address(request):
	firstname = request.form['firstname'];
	if 'firstname' not in request.form or 'lastname' not in request.form or 'phone_number' not in request.form \
		or 'contact_number' not in request.form: 
		return; 
	
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
	except Exception, e:
		db.session.rollback()
		print str(e);
		# db.session.flush();
		raise ValueError(str(e));
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
	res = {'msg':'something went wrong sorry'}
	try:
		patient_addr = add_address(request);
		if patient_addr is None:
			res['msg'] = 'Could not create patient address, please try again'
			return res;
	except ValueError as err:
		res['msg'] = str(err.args)
		return res 
	auth = request.authorization
	if auth.username:
		manager = Manager.query.filter(Manager.id == int(auth.username))
		if manager == None:
			res['msg'] = "sorry incorrect manager id, please resend form"
			return res;
		else:
			try:
				patient = Patient(request.form['firstname'], request.form['lastname'], request.form['phone_number'], 
					request.form['contact_number'], patient_addr.id, auth.username);
				
#	message = client.messages.create(to=request.form['phone_number'], from_=request.form['phone_number'],body=add_patient_message)
#				message = "Thanks for joining Speranza Health"

#				r = requests.post(FRONTLINESMS_WEBHOOK, json={"apiKey": FRONTLINESMS_API_KEY, 
#					"payload":{"message": message, "recipients":[{"type": "mobile", "value": request.form['phone_number']}]}});
				print request.form['phone_number']
				db.session.add(patient);
				db.session.commit();
				res['msg'] = 'success'
				res['patient_id'] = patient.id
				print res
				return res;
			except Exception, e:
				db.session.flush();
				res['msg'] = str(e) 
				return res;

def add_manager(request):
	res = {'msg':'Something has gone wrong'}
	try:
		addr = add_address(request);
		if addr is None:
			res['msg'] = "something has gone wrong creating an address, please try again"
			return res;
	except ValueError as err:
		res['msg'] = str(err.args)
		return res; 
	
	if request.form.has_key('password'):
		manager = Manager(request.form['firstname'], request.form['lastname'],
			       	request.form['phone_number'], request.form['contact_number'], 
				addr.id, request.form['password']);
		try:
			db.session.add(manager);
			db.session.commit();
		except ValueError as err:
			db.session.flush();
			res['msg'] = str(err.args);
			return res;

		res['msg'] = 'success'
		res['mgr_id'] = manager.id
		print "message: " + res['msg']
		return res
	else:
		res['msg'] = 'No password entered'
		return res;

def get_managers(request):
	managers = Manager.query.all();
	return managers;

def get_patients(request):
	pts = Patient.query.all();
	return pts;
def get_appts(request):
	return Appointment.query.all();
def verify_password(username, password_or_token):
	mgr = Manager.verify_auth_token(password_or_token)
	print "mgr after verify_auth_token: "
	print mgr
	if not mgr:
		mgr = Manager.query.filter(Manager.id == username).first();
		if not mgr or not mgr.verify_password(password_or_token):
			return False;
	g.manager= mgr 
	return True;

def get_user_appts(request):
	import json
	try:
		res = {'msg':'Sorry something went wrong'}
		auth = request.authorization
		import datetime
		timestamp = datetime.date.today()
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)
		patients = Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id);
		appts = []
		for val in patients:
			appt = Appointment.query.filter(Appointment.user_id == val.id).filter(Appointment.date >= timestamp).filter(Appointment.date < tomorrow)
			if(appt.first() is not None):
				appts.append(appt.first())
		res['msg'] = 'success'
		res['appts'] = appts
		return res;
	except ValueError, e:
		db.session.rollback();
		res['msg'] = str(e) 
		return res;

def edit_patient(request):
	res = {'msg':"something has gone wrong"};
	if 'user_id' not in request.form:
		res['msg'] = "Could not edit patient, missing user_id in form";
		return res;
	else:
		try:
			auth = request.authorization;
			user = Patient.query.filter(Patient.id == request.form['user_id']).first();
			if user is None:
				res['msg'] = "Invalid patient id"
				return res;
			if user.manager_id != int(auth.username):
				res['msg'] = "Invalid manager"
				return res;
			if 'phone_number' in request.form:
				user.phone_number = request.form['phone_number']
			if 'contact_number' in request.form:
				user.contact_number = request.form['contact_number']
			if 'edit_address' in request.form:
				addr_res = edit_patient_address(request);
				if addr_res['msg'] != "success":
					res['msg'] = addr_res['msg']
					return res;
			try:
				db.session.commit();
				res['msg'] = "success"
				return res;
			except:
				db.session.rollback();
				res['msg'] = "Something went wrong, couldn't update"
				return res;
		except:
			res['msg'] = "Something went wrong trying to fetch your user_id please try again"
			return res;
def edit_patient_address(request):
	res = {'msg':'something has gone wrong'};
	if 'user_id' not in request.form:
		res['msg'] = "Could not edit patient, missing user_id in form";
		return res;
	else:
		user = Patient.query.filter(Patient.id == request.form['user_id']).first();
		if user is None:
			res['msg'] = "something went wrong"
			return res;
		address = Address.query.filter(Address.id == user.address_id).first()
		if address is None:
			res['msg'] = "Something went wrong fetching the address"
			return res;
		if 'street_num' in request.form:
			address.street_num = request.form['street_num']
		if 'street_name' in request.form:
			address.street_name = request.form['street_name']
		if 'street_type' in request.form:
			address.street_type = request.form['street_type']
		if 'city_name' in request.form:
			address.city_name = request.form['city_name']
		if 'zipcode' in request.form:
			address.zipcode = request.form['zipcode']
		if 'district' in request.form:
			address.district = request.form['district']
		try:
			db.session.commit();
			res['msg'] = "success";
			return res;
		except:
			db.session.rollback();
			return res;	

def edit_appt(request):
	res = {'msg':'something has gone wrong'};
	if 'user_id' not in request.form or 'old_date' not in request.form:
		res['msg'] = "Could not edit appt, missing user_id or date in form";
		return res;
	else:
		import datetime
		timestamp = datetime.datetime.utcfromtimestamp(int(request.form['old_date']));
		appt = Appointment.query.filter(Appointment.user_id == request.form['user_id']).filter(Appointment.date == timestamp).first()
		if appt is None:
			res['msg'] = "Either user id or date is wrong"
			return res;
		changed = False;
		if 'new_date' in request.form:
			new_timestamp = datetime.datetime.utcfromtimestamp(int(request.form['new_date']));
			appt.date = new_timestamp 
			changed = True;
		if 'appt_type' in request.form:
			appt.appt_type = request.form['appt_type']
			changed = True;
		try:
			if changed == True:
				db.session.commit();
			res['msg'] = "success";
			return res;
		except ValueError, e:
			res['msg'] = str(e)
			db.session.rollback();
			return res;

def delete_appt(request):
	res = {'msg':'something has gone wrong'};
	if 'user_id' not in request.form or 'date' not in request.form:
		res['msg'] = "Could not delete appt, missing user_id or date in form";
		return res;
	else:
		import datetime
		timestamp = datetime.datetime.utcfromtimestamp(int(request.form['date']));
		appt = Appointment.query.filter(Appointment.user_id == request.form['user_id']).filter(Appointment.date == timestamp)
		if appt.first() is None:
			res['msg'] = "Either user_id or date is wrong"
			return res;
		try:
			appt.delete();
			db.session.commit();
			res['msg'] = 'success';
			return res;
		except ValueError, e:
			res['msg'] = str(e) 
			return res;	

def delete_patient(request):
	res = {'msg':'something has gone wrong'}
	if 'user_id' not in request.form:
		res['msg'] = "Could not delete patient, missing user_id in form";
		return res;
	auth = request.authorization
	user = Patient.query.filter(Patient.id == request.form['user_id'])
	if user.first() is None:
		res['msg'] = 'invalid user id'
		return res;
	if user.first().manager_id != int(auth.username):
		res['msg'] = 'invalid manager id'
		return res;	
	try:
		user.delete();
		db.session.commit();
		res['msg'] = 'success'
		return res;
	except:
		res['msg'] = "delete failed"
		return res;	
		
