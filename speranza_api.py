from application.models import *
from flask import Flask, request, redirect, jsonify, g, abort
import sqlalchemy.exc
from dateutil import parser
import requests
from messenger import send_message
from helpers import get_form_data

GUAT_COUNTRY_CODE = '502'
USA_COUNTRY_CODE = '1'

# TODO make this more robust
def sanitize_phone_number(number):
#	print 'pre-sanitized', number
#	print len(number)
	new_number = ''
	if len(number) == 8:
		new_number = GUAT_COUNTRY_CODE + str(number)
	else:
		new_number = str(number)
#	print 'post-sanitized', new_number
	return int(new_number)
def verify_manager_access(patient, auth):
	manager = Manager.query.filter(Manager.id == int(auth.username))
	return patient.grant_access(manager.org_id)
def add_appt(request):
	res = {'msg':'Sorry something went wrong'}
	form_data = get_form_data(request)

	if 'user_id' in form_data and 'date' in form_data and 'appt_type' in form_data:
		#error check that manager making appt is the patient's manager
		patient = Patient.query.filter(Patient.id == form_data['user_id']).first();
		if patient is None:
			abort(422, "La identificacion del paciente es incorrecto");
		if len(form_data['appt_type']) == 0:
			abort(422, "El appt_type es incorrecto");

		if verify_manager_access(patient, request.authorization) == False:
			abort(401, "La identificacion del gerente es incorrecto"); 
		try:
			#right now storing everything as a datetime, but we need to be consistent about this
			import datetime
			timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']));
			exists = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(Appointment.date == timestamp);

			if exists.first() is not None:
				abort(422, "Ya existe una cita para este fecha");

			new_appt = Appointment(form_data['user_id'], (int)auth.username, timestamp, form_data['appt_type']);
			db.session.add(new_appt);
			db.session.commit();
			res['msg'] = 'success'
		except sqlalchemy.exc.DatabaseError, e:
			db.session.rollback()
			abort(500, str(e))
			#db.session.flush();
			return res;
		return res;
	else:
		abort(422, "Necesitamos mas informacion, intenta otra vez por favor");

def checkin_out(request, checkin = True):
	res = {'msg':'Sorry something went wrong'}
	form_data = get_form_data(request)

	if 'user_id' in form_data and 'date' in form_data:
		patient = Patient.query.filter(Patient.id == form_data['user_id']).first();
		if patient is None:
			abort(422, "La identificacion del paciente es incorrecto");

		if verify_manager_access(patient, request.authorization) == False:
			abort(401, "La identificacion del gerente es incorrecto");

		try:
			import datetime
			timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
			appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(Appointment.date == timestamp).first()
			if appt is None:
				abort(422, "La fecha es incorrecto, intenta otra vez por favor");
			if checkin == True:
				if appt.checkin == True:
					abort(422, "Ya comprobado para este cita")
				appt.checkin = True;
			else:
				if appt.checkout == True:
					abort(422, "Ya desprotegido")
				appt.checkout = True;
			db.session.commit();
			res['msg'] = 'success'
			return res;
		except sqlalchemy.exc.DatabaseError, e:
			abort(500, str(e))
	else:
		abort(422, "Necesita mas informacion, intenta otra vez por favor")
		
#returns False if invalid request, True otherwise
def verify_new_user(request):
	form_data = get_form_data(request)

	if 'firstname' not in form_data or 'lastname' not in form_data or 'phone_number' not in form_data \
		or 'contact_number' not in form_data: 
		if 'firstname' not in form_data:
			abort(422, "missing firstname")
		if 'lastname' not in form_data:
			abort(422,"missing lastname")
		if 'phone_number' not in form_data:
			abort(422, "missing phone_number")
		if 'contact_number' not in form_data:
			abort(422, "missing contact_number")
	if len(form_data['firstname']) == 0 or len(form_data['lastname']) == 0:
		abort(422, "names are too short")
	pn = form_data['phone_number'];
	cn = form_data['contact_number'];
#	if pn.isdigit() == False or cn.isdigit() == False or (len(pn) == 0) or (len(cn) == 0):
#		print "phone number isn't digit"
#		return False;

#returns Address if valid, otherwise raises an error
def add_address(request):
	form_data = get_form_data(request)

	user_addr = Address();
	if form_data.has_key('street_num'):
		user_addr.street_num = form_data['street_num'];
	if form_data.has_key('street_name'):
		user_addr.street_name = form_data['street_name'];
	if form_data.has_key('street_type'):
		user_addr.street_type = form_data['street_type'];
	if form_data.has_key('city_name'):
		user_addr.city_name = form_data['city_name'];
	if form_data.has_key('zipcode'):
		user_addr.zipcode = form_data['zipcode'];
	if form_data.has_key('district'):
		user_addr.district = form_data['district'];
	
	try:
		print 'attempting to add address'
		db.session.add(user_addr);
		db.session.flush();
	except Exception, e:
		print 'exception adding address ', str(e)
		db.session.rollback()
		# db.session.flush();
		raise ValueError(str(e));
	return user_addr;

def add_patient(request):
	res = {'msg':'something went wrong sorry'}
	form_data = get_form_data(request)
	verify_new_user(request)
	if 'dob' not in form_data:
		abort(422, 'Necesita dob, intenta otra vez')
	if 'gov_id' not in form_data:
		abort(422,'Necesita identificacion, intenta otra vez')
	try:
		patient_addr = add_address(request);
		if patient_addr is None:
			abort(500, 'Tenemos una problema con la aplicacion, por favor intenta otra vez')
	except ValueError as err:
		abort(500, str(err.args))
	auth = request.authorization
	if auth.username:
		manager = Manager.query.filter(Manager.id == int(auth.username))
		if manager == None:
			abort(401, 'La identificacion para el gerente es incorecto, por favor intenta otra vez')
		else:
			try:
				# #right now storing everything as a datetime, but we need to be consistent about this
				# import datetime
				# dob = datetime.datetime.utcfromtimestamp(float(form_data['dob']));
				patient_phone_number = sanitize_phone_number(form_data['phone_number'])
				patient_contact_number = sanitize_phone_number(form_data['contact_number'])
				patient = Patient(form_data['firstname'], form_data['lastname'], patient_phone_number, 
					patient_contact_number, patient_addr.id, auth.username, form_data['dob'], form_data['gov_id']);
#	message = client.messages.create(to=form_data['phone_number'], from_=form_data['phone_number'],body=add_patient_message)
				message = "Gracias para unir Speranza Health"

				r = send_message(message, patient.contact_number)
#				print r

				#add patient to organization
				patient.organizations.append(manager.org_id);	 

				db.session.add(patient);
				db.session.commit();
				res['msg'] = 'success'
				res['patient_id'] = patient.id
				res['patient_contact_number'] = patient.contact_number
#				print res
				return res;
			except Exception, e:
				db.session.flush();
				abort(500, str(e))

def add_manager(request):
	res = {'msg':'Something has gone wrong'}
	form_data = get_form_data(request)
	
	verify_new_user(request) 
	try:
		addr = add_address(request);
		if addr is None:
			abort(500, "Hay una problema con el server, por favor intenta otra vez")
	except ValueError as err:
		abort(500, str(err.args))

	if form_data.has_key('password'):
		phone_number = sanitize_phone_number(form_data['phone_number'])
		contact_number = sanitize_phone_number(form_data['contact_number'])
		manager = Manager(form_data['firstname'], form_data['lastname'],
			       	phone_number, contact_number, 
				addr.id, form_data['password']);
		try:
			db.session.add(manager);
			db.session.commit();
		except ValueError as err:
			db.session.flush();
			abort(500, str(err.args))

		res['msg'] = 'success'
		res['mgr_id'] = manager.id
		return res
	else:
		#TODO check spanish for password
		abort(422, "Necesita una contrasena")

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
	if not mgr:
		mgr = Manager.query.filter(Manager.id == username).first();
		if not mgr or not mgr.verify_password(password_or_token):
			return False;
	g.manager= mgr 
	return True;

def get_user_appts(request):
	import json
	form_data = get_form_data(request)

	try:
		res = {'msg':'Sorry something went wrong'}
		auth = request.authorization
		import datetime
		today = datetime.date.today()
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)
		pts = Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id);

		#TODO: broken
		#appts = Appointment.query.filter(Appointment.user_id.in_(Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id))).filter(Appointment.date >= today).filter(Appointment.date < tomorrow).join(Patient, (Patient.id == Appointment.user_id)).with_entities(Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()
		
		appts = Appointment.query.filter(Appointment.manager_id == int(auth.username)).filter(Appointment.date >= today).filter(Appointment.date < tomorrow).join(Patient, (Patient.id == Appointment.user_id)).with_entities(Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()

		ser_appts = []	
		for appt in appts:
			ser_appt = {'firstname':appt.firstname, 'lastname':appt.lastname, 'date':appt.date, 'appt_type':appt.appt_type}
			ser_appts.append(ser_appt)

		res['msg'] = 'success'
		res['appts'] = ser_appts
		return res;
	except ValueError, e:
		db.session.rollback();
		abort(500, str(e));

def edit_patient(request):
	res = {'msg':"something has gone wrong"};
	form_data = get_form_data(request)

	if 'user_id' not in form_data:
		abort(422, "No podemos editar el paciente, necesita user_id")
	else:
		try:
			auth = request.authorization;
			user = Patient.query.filter(Patient.id == form_data['user_id']).first();
			if user is None:
				abort(422,  "Invalid patient id")

			if verify_manager_access(user, auth) == False:
				abort(422,  "Invalid manager")
			if 'phone_number' in form_data:
				if form_data['phone_number'].isdigit() == False or (len(form_data['phone_number']) == 0):
					abort(422, 'Please enter a valid phone number')
				user.phone_number = form_data['phone_number']
			if 'contact_number' in form_data:
				if form_data['contact_number'].isdigit() == False:
					abort(422, 'Please enter a valid contact number')
					return res;
				user.contact_number = form_data['contact_number']
			if 'edit_address' in form_data:
				edit_patient_address(request);
			if 'dob' in form_data:
				user.dob = form_data['dob']
			try:
				db.session.commit();
				res['msg'] = "success"
				return res;
			except:
				db.session.rollback();
				abort(500, "Something went wrong, couldn't update")
		except ValueError, e:
			abort(500, "Something went wrong trying to fetch your user_id please try again")

def find_patient(request):
	res = {'msg':'something has gone wrong'};
	form_data = get_form_data(request)
	if 'firstname' in form_data and 'lastname' in form_data and 'dob' in form_data:
		patients = Patient.query.filter(Patient.firstname == form_data['firstname']).filter(Patient.lastname == form_data['lastname']).filter(Patient.dob == form_data['dob']);
	elif 'gov_id' in form_data:
		patients = Patient.query.filter(Patient.gov_id == int(form_data['gov_id']))
	else:
		abort(422, 'Necesitamos mas informacion sobre el paciente, por favor hacer otra vez')

	ser_patients = [];
	for patient in patients:
		address = Address.query.filter(Address.id == patient.address_id).first()
		manager = Manager.query.filter(Manager.id == patient.manager_id).first()
		ser_pt= {'firstname':patient.firstname, 'lastname':patient.lastname, 'phone_number':patient.phone_number, 
				 'contact_number':patient.contact_number, 'street_num':address.street_num, 'street_name':address.street_name,
				 'street_type':address.street_type, 'city_name':address.city_name, 'zipcode':address.zipcode, 'district':address.district,
				 'manager_firstname':manager.firstname, 'manager_lastname':manager.lastname, 'manager_phone_number':manager.phone_number, 
				 'manager_contact_number':manager.contact_number, 'dob':patient.dob, 'gov_id':patient.gov_id, 'patient_id':patient.id}
		ser_patients.append(ser_pt)

	if len(ser_patients) == 0:
		abort(422, "No hay pacientes con este informacion")	

	res['msg'] = 'success'
	res['patients'] = ser_patients
	return res;

def edit_patient_address(request):
	res = {'msg':'something has gone wrong'};
	form_data = get_form_data(request)

	if 'user_id' not in form_data:
		abort(422, "Could not edit patient, missing user_id in form")
	else:
		user = Patient.query.filter(Patient.id == form_data['user_id']).first();
		if user is None:
			abort(500,  "something went wrong")
		address = Address.query.filter(Address.id == user.address_id).first()
		if address is None:
			abort(500, "Something went wrong fetching the address")
		if 'street_num' in form_data:
			address.street_num = form_data['street_num']
		if 'street_name' in form_data:
			address.street_name = form_data['street_name']
		if 'street_type' in form_data:
			address.street_type = form_data['street_type']
		if 'city_name' in form_data:
			address.city_name = form_data['city_name']
		if 'zipcode' in form_data:
			address.zipcode = form_data['zipcode']
		if 'district' in form_data:
			address.district = form_data['district']
		try:
			db.session.commit();
		except:
			db.session.rollback();
			abort(500, "something went wrong")

def edit_appt(request):
	res = {'msg':'something has gone wrong'};
	form_data = get_form_data(request)

	if 'user_id' not in form_data or 'old_date' not in form_data:
		abort(422, "Could not edit appt, missing user_id or date in form")
	else:
		import datetime
		timestamp = datetime.datetime.utcfromtimestamp(int(form_data['old_date']));
		appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(Appointment.date == timestamp).first()
		if appt is None:
			abort(422, "Necesitamos la identificacion del usario o la fecha")
		changed = False;
		if 'new_date' in form_data:
			new_timestamp = datetime.datetime.utcfromtimestamp(int(form_data['new_date']));
			appt.date = new_timestamp 
			changed = True;
		if 'appt_type' in form_data:
			appt.appt_type = form_data['appt_type']
			changed = True;
		try:
			if changed == True:
				db.session.commit();
			res['msg'] = "success";
			return res;
		except ValueError, e:
			db.session.rollback();
			abort(500, str(e));

def delete_appt(request):
	res = {'msg':'something has gone wrong'};
	form_data = get_form_data(request)

	if 'user_id' not in form_data or 'date' not in form_data:
		abort(422, "No podemos borrar la cita, necesitamos la identificacion del usario o la fecha") 
	else:
		import datetime
		timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']));
		appt = Appointment.query.filter(Appointment.user_id == form_data['user_id']).filter(Appointment.date == timestamp)
		if appt.first() is None:
			abort(422, "Necesitamos la identificacion del usario o la fecha")
		try:
			appt.delete();
			db.session.commit();
			res['msg'] = 'success';
			return res;
		except ValueError, e:
			db.session.rollback();
			abort(500, str(e))

def delete_patient(request):
	res = {'msg':'something has gone wrong'}
	form_data = get_form_data(request)

	if 'user_id' not in form_data:
		abort(422, "No podemos borrar el paciente,  necesitamos la identificacion del usario")
	auth = request.authorization
	user = Patient.query.filter(Patient.id == form_data['user_id'])
	if user.first() is None:
		abort(422, "La identificacion es incorrecto")
	if verify_manager_access(patient, auth) == False:
		abort(422, "La identificacion del gerente es incorrecto") 
	try:
		user.delete();
		db.session.commit();
		res['msg'] = 'success'
		return res;
	except:
		abort(500,  "borrar ha fallado")
