from application.models import *
from flask import Flask, request, redirect, jsonify, g, abort
import sqlalchemy.exc
from dateutil import parser
import requests
from messenger import send_message
from helpers import * 
from verification import *
import datetime
from mixpanel import Mixpanel

MIXPANEL_TOKEN = '9356a2c2986506360e6ba9929a516f16'
mp = Mixpanel(MIXPANEL_TOKEN)

DEBUG = False;

def add_appt(request):
	res = {'msg':'Sorry something went wrong'}
	form_data = get_form_data(request, DEBUG)
	requirements = ['user_id', 'date', 'appt_type']
	if verify_form_data(requirements, form_data):
		#error check that manager making appt is the patient's manager
		if verify_patient_exists(form_data['user_id']) is False:
			abort(422, "La identificacion del paciente es incorrecto");
		if len(form_data['appt_type']) == 0:
			abort(422, "El appt_type es incorrecto");

		if verify_manager_access(form_data['user_id'], request.authorization) == False:
			abort(401, "La identificacion del gerente es incorrecto"); 
		try:
			#right now storing everything as a datetime, but we need to be consistent about this
			timestamp = datetime.datetime.utcfromtimestamp(int(form_data['date']));
			exists = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(Appointment.date == timestamp);

			if exists.first() is not None:
				abort(422, "Ya existe una cita para este fecha");

			new_appt = Appointment(form_data['user_id'], int(request.authorization.username), timestamp, form_data['appt_type']);
			db.session.add(new_appt);
			db.session.commit();
			res['msg'] = 'success'
			if DEBUG == False:
				mp.track(form_data['user_id'], "New appointment added", properties={'date':timestamp, 'appt_type':form_data['appt_type']})
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
	form_data = get_form_data(request, DEBUG)
	requirements = ['user_id', 'date']
	if verify_form_data(requirements, form_data):

		if verify_patient_exists(form_data['user_id']) == False:
			abort(422, "La identificacion del paciente es incorrecto");

		if verify_manager_access(form_data['user_id'], request.authorization) == False:
			abort(401, "La identificacion del gerente es incorrecto");

		try:
			timestamp = datetime.datetime.utcfromtimestamp(float(form_data['date']))
			appt = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(Appointment.date == timestamp).first()
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
			if DEBUG == False:
				if checkin == True:
					mp.track(form_data['user_id'], "Patient checked in", properties={'date':timestamp})
				else:
					mp.track(form_data['user_id'], "Patient checked out", properties={'date':timestamp})

			return res;
		except sqlalchemy.exc.DatabaseError, e:
			abort(500, str(e))
	else:
		abort(422, "Necesita mas informacion, intenta otra vez por favor")
		
#returns Address if valid, otherwise raises an error
def add_address(request):
	form_data = get_form_data(request, DEBUG)
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
		db.session.add(user_addr);
		db.session.commit();
	except Exception, e:
		print 'exception adding address ', str(e)
		db.session.rollback()
		# db.session.flush();
		raise ValueError(str(e));
	return user_addr;

def add_patient(request):
	res = {'msg':'something went wrong sorry'}
	form_data = get_form_data(request, DEBUG)
	required_args = ['firstname', 'lastname', 'phone_number', 'contact_number', 'dob', 'gov_id', 'city_name']
	if(verify_form_data(required_args, form_data) == False):
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	verify_new_user(form_data)
	try:
		patient_addr = add_address(request);
		if patient_addr is None or patient_addr.id is None:
			abort(500, 'Tenemos una problema con la aplicacion, por favor intenta otra vez')
	except ValueError as err:
		abort(500, str(err.args))
	auth = request.authorization
	if auth.username:
		manager = Manager.query.filter(Manager.id == int(auth.username)).first()
		if manager == None:
			abort(401, 'La identificacion para el gerente es incorecto, por favor intenta otra vez')
		else:
			# #right now storing everything as a datetime, but we need to be consistent about this
			# dob = datetime.datetime.utcfromtimestamp(float(form_data['dob']));
			patient_phone_number = sanitize_phone_number(form_data['phone_number'])
			patient_contact_number = sanitize_phone_number(form_data['contact_number'])
			patient = Patient(form_data['firstname'], form_data['lastname'], patient_phone_number, 
				patient_contact_number, patient_addr.id, form_data['dob'], form_data['gov_id']);
#	message = client.messages.create(to=form_data['phone_number'], from_=form_data['phone_number'],body=add_patient_message)
			message = "Gracias para unir Speranza Health"

			r = send_message(message, patient.contact_number, DEBUG)
#			print r

			#add patient to organization
			manager_org = Organization.query.filter(Organization.id == manager.org_id).first()
			patient.organizations.append(manager_org);	 

			try:
				db.session.add(patient);
				db.session.commit();
				if DEBUG == False:
					mp.track(auth.username, "Patient added", properties={'firstname':form_data['firstname'], 'lastname':form_data['lastname'], 'dob':form_data['dob'], 'gov_id':form_data['gov_id']})
			except Exception, e:
				abort(500, str(e))

			res['msg'] = 'success'
			res['patient_id'] = patient.id
			res['patient_contact_number'] = patient.contact_number
#			print res
			return res;

def add_manager(request):
	res = {'msg':'Something has gone wrong'}
	form_data = get_form_data(request, DEBUG)

	requirements = ['firstname', 'lastname', 'password', 'phone_number', 'email']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	if verify_new_user(form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")

	phone_number = sanitize_phone_number(form_data['phone_number'])
	manager = Manager(form_data['firstname'], form_data['lastname'],
		       	phone_number, form_data['email'], form_data['password']);
	try:
		db.session.add(manager);
		db.session.commit();
		if DEBUG == False:
			mp.track(manager.id, "Manager added", properties={'firstname':form_data['firstname'], 'lastname':form_data['lastname']})
	except ValueError as err:
		db.session.flush();
		abort(500, str(err.args))

	res['msg'] = 'success'
	res['mgr_id'] = manager.id
	return res

def get_managers(request):
	managers = Manager.query.all();
	return managers;

def get_patients(request):
	pts = Patient.query.all();
	return pts;

def get_appts(request):
	return Appointment.query.all();

def get_user_appts(request):
	#	import json
	form_data = get_form_data(request, DEBUG)

	res = {'msg':'Sorry something went wrong'}
	auth = request.authorization
	today = datetime.date.today()
	tomorrow = datetime.date.today() + datetime.timedelta(days=1)
#	try:
#		pts = Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id);
#	except ValueError, e:
#		db.session.rollback();
#		abort(500, str(e));

		#TODO: broken
		#appts = Appointment.query.filter(Appointment.user_id.in_(Patient.query.filter(Patient.manager_id == int(auth.username)).with_entities(Patient.id))).filter(Appointment.date >= today).filter(Appointment.date < tomorrow).join(Patient, (Patient.id == Appointment.user_id)).with_entities(Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()
	try:	
		appts = Appointment.query.filter(Appointment.manager_id == int(auth.username)).filter(Appointment.date >= today).filter(Appointment.date < tomorrow).join(Patient, (Patient.id == Appointment.patient_id)).with_entities(Patient.id, Patient.firstname, Patient.lastname, Appointment.date, Appointment.appt_type).all()
	except ValueError, e:
		db.session.rollback();
		abort(500, str(e))

	ser_appts = []	
	for appt in appts:
		ser_appt = {'patient_id':appt.id, 'firstname':appt.firstname, 'lastname':appt.lastname, 'date':appt.date, 'appt_type':appt.appt_type}
		ser_appts.append(ser_appt)

	res['msg'] = 'success'
	res['appts'] = ser_appts
	return res;

def edit_patient(request):
	res = {'msg':"something has gone wrong"};
	form_data = get_form_data(request, DEBUG)

	requirements = ['user_id']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	if verify_manager_access(form_data['user_id'], request.authorization) == False:
		abort(401, "La identificacion del gerente es incorrecto");
	else:
		try:
			user = Patient.query.filter(Patient.id == form_data['user_id']).first();
			if user is None:
				abort(422,  "Invalid patient id")
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
	form_data = get_form_data(request, DEBUG)
	if 'firstname' in form_data and 'lastname' in form_data and 'dob' in form_data:
		patients = Patient.query.filter(Patient.firstname == form_data['firstname']).filter(Patient.lastname == form_data['lastname']).filter(Patient.dob == form_data['dob']);
	elif 'gov_id' in form_data:
		patients = Patient.query.filter(Patient.gov_id == int(form_data['gov_id']))
	else:
		abort(422, 'Necesitamos mas informacion sobre el paciente, por favor hacer otra vez')

	mgr_patients = [];
	for patient in patients:
		if(verify_manager_access(patient.id, request.authorization)):
			mgr_patients.append(patient)

	if len(mgr_patients) == 0:
		abort(422, "No hay pacientes con este informacion")	

	res['msg'] = 'success'
	res['patients'] = mgr_patients 
	return res;

def edit_patient_address(request):
	res = {'msg':'something has gone wrong'};
	form_data = get_form_data(request, DEBUG)

	requirements = ['user_id']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
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
	form_data = get_form_data(request, DEBUG)
	requirements = ['user_id', 'old_date']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	else:
		timestamp = datetime.datetime.utcfromtimestamp(int(form_data['old_date']));
		appt = Appointment.query.filter(Appointment.patient_id== form_data['user_id']).filter(Appointment.date == timestamp).first()
		if appt is None:
			abort(422, "No hay una cita para este paciente y fecha")
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
	form_data = get_form_data(request, DEBUG)

	requirements = ['user_id', 'date']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "Necesita mas informaction, intenta otra vez por favor")
	else:
		timestamp = datetime.datetime.utcfromtimestamp(int(form_data['date']));
		appt = Appointment.query.filter(Appointment.patient_id == form_data['user_id']).filter(Appointment.date == timestamp)
		if appt.first() is None:
			abort(422, "No hay una cita para este paciente y fecha")
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
	form_data = get_form_data(request, DEBUG)

	requirements = ['user_id']
	if verify_form_data(requirements, form_data) == False:
		abort(422, "No podemos borrar el paciente,  necesitamos la identificacion del usario")
	auth = request.authorization
	user = Patient.query.filter(Patient.id == form_data['user_id'])
	if user.first() is None:
		abort(422, "La identificacion es incorrecto")
	if verify_manager_access(user.first().id, auth) == False:
		abort(422, "La identificacion del gerente es incorrecto") 
	try:
		user.delete();
		db.session.commit();
		res['msg'] = 'success'
		return res;
	except:
		db.session.rollback()
		abort(500,  "borrar ha fallado")
