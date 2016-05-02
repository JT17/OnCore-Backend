from application.models import *
from flask import Flask, request, redirect, jsonify, g

def add_appt(request):
	if 'user_id' in request.form and 'date' in request.form and 'appt_type' in request.form:
		#error check that manager making appt is the patient's manager
		patient = Patient.query.filter(Patient.id == request.form['user_id']).first();
		if patient is None:
			return str("Bad patient id")
		auth = request.authorization
		if patient.manager_id != int(auth.username):
			return str("Wrong manager");
		try:
			import datetime
			timestamp = datetime.datetime.fromtimestamp(int(request.form['date']));
			new_appt = Appointment(request.form['user_id'], timestamp, request.form['appt_type']);
			db.session.add(new_appt);
			db.session.commit();
		except Exception, e:
			print str(e);
			db.session.rollback()
			#db.session.flush();
			print "wrong"
			return str("Could not create new appt :( something went wrong");
		return str("success");
	else:
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
	auth = request.authorization
	if auth.username:
		manager = Manager.query.filter(Manager.id == int(auth.username))
		if manager == None:
			return str("Sorry incorrect manager id, please resend form")
		else:
			patient = Patient(request.form['firstname'], request.form['lastname'], request.form['phone_number'],
					request.form['contact_number'], patient_addr.id, int(auth.username));
			try:
				db.session.add(patient);
				db.session.commit();
			except:
				db.session.flush();
				raise ValueError("Could not create patient, something went wrong sorry");
	else:
		return str("Need a manager");
	return str("success")


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
		res = {"msg":"success", "mgr_id" : manager.id}
		print "message: " + res['msg']
		return res
	else:
		return str("No password entered");

def get_managers(request):
	managers = Manager.query.all();
	return managers;
def get_patients(request):
	pts = Patient.query.all();
	return pts;

def verify_password(username, password_or_token):
	mgr = Manager.verify_auth_token(password_or_token)
	if not mgr:
		mgr = Manager.query.filter_by(id = username).first();
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
		print type(user)
		if user is None:
			return str("Invalid user id");
		if user.manager_id != int(auth.username):
			return str("Invalid manager id");	
		appts = Appointment.query.filter(Appointment.user_id == request.form['user_id'])
		all_appts = Appointment.query.order_by(Appointment.date).all()
		for val in all_appts:
			print val.user_id
		return all_appts 
	except ValueError:
		return str("Couldn't fetch your appointments something went wrong :(");
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
def delete_patient(request):
	res = {'msg':'something has gone wrong'}
	if 'user_id' not in request.form:
		res['msg'] = "Could not delete patient, missing user_id in form";
		return res;
	auth = request.authorization
	user = Patient.query.filter(Patient.id == request.form['user_id'])
	print type(user)
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
		
