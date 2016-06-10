from application.models import *
from flask import Flask, request, redirect, jsonify, g
import datetime
import requests

# FRONTLINESMS_API_KEY = "309fefe6-e619-4766-a4a2-53f0891fde23"
# FRONTLINESMS_WEBHOOK = "https://cloud.frontlinesms.com/api/1/webhook"
# -*- coding: utf-8 -*-
import plivo

auth_id = "MAY2ZKYMZHNJZMN2Q4NT"
auth_token = "YzFjM2E5ODFhNzM3YzIyMmI3NmU0N2FhZmM5ODgw"
src_phone = '+18057424820'

p = plivo.RestAPI(auth_id, auth_token)

def send_message(message, phone_number):
	params = {
	    'src': src_phone, # Sender's phone number with country code
	    'dst' : phone_number, # Receiver's phone Number with country code
	    'text' : message, # Your SMS Text Message - English
	#    'url' : "http://example.com/report/", # The URL to which with the status of the message is sent
	    'method' : 'POST' # The method used to call the url
	}

	response = p.send_message(params)

	# Prints the complete response
	print params
	print str(response)
	return response

	# r = requests.post(FRONTLINESMS_WEBHOOK, json={"apiKey": FRONTLINESMS_API_KEY, 
	# 	"payload":{"message": message, "recipients":[{"type": "mobile", "value": '+'+str(phone_number)}]}});
	# return r;

def send_appointment_reminders_no_authentication():
	import json
	try:
		all_appts = Appointment.query.all()
		for appt in all_appts:
			if appt.checkin or appt.checkout:
				continue
			# print appt.user_id
			# print appt.date
			# print datetime.datetime.now() # TODO maybe should be utcnow?
			time_until_appointment = appt.date - datetime.datetime.now()
			print time_until_appointment
		 	if time_until_appointment <= datetime.timedelta(days=1):
		 		patient = Patient.query.filter(Patient.id == appt.user_id).first()
		 		message = "Hola {0}, \n no olvide que tiene una cita a las {1}".format(patient.firstname, str(appt.date))
		 		if time_until_appointment <= datetime.timedelta(days=0):
		 			message = "LATE APPONTMENT: " + message
		 		print "Message: {0} \nNumber: {1} \nDate: {2}".format(message, patient.phone_number, appt.date)
				send_message(message, patient.phone_number);
	except ValueError:
		return str("Couldn't fetch your appointments something went wrong :(");

def send_diabetes_reminders():
	try:
		db_pt_noinsulin = Appointment.query.filter(Appointment.appt_type == 'no insulina');
		for appt in db_pt_noinsulin:
			patient = Patient.query.filter(Patient.id == appt.user_id).first()
			message = "Hi {0}, \n realice su dieta, no olvide comer fruitas y verduras cada dia".format(patient.firstname)
			send_message(message, patient.phone_number);
		db_pt_insulin = Appointment.query.filter(Appointment.appt_type == 'insulina');
		for appt in db_pt_insulin:
			patient = Patient.query.filter(Patient.id == appt.user_id).first();
			message = "Hi {0}, \n no olvide que necesita injectarse su insulina hoy, 30 minutos antes de tu desayuno y cena".format(patient.firstname)
			send_message(message, patient.phone_number);

	except ValueError, e:
		return str(e);

def is_number(s):
	try:
		float(s)
		return True;
	except ValueError:
		return False

def send_hemeonc_reminders():
	try:
		treatment_file = open('hemeonc_reminders.txt','r');
		treatment = ""
		messages = {}
		for line in treatment_file:
			if line.rstrip('\n') == 'TREATMENT_TYPE':
				treatment = next(treatment_file).rstrip('\n').lower();	
				messages = {};
			elif is_number(line) == True:
				t_message = next(treatment_file);
				messages[int(line)] = t_message
			elif line.rstrip('\n') == 'END_TREATMENT':
				print "inside end_treatment"
				print treatment
				appts = Appointment.query.filter(Appointment.appt_type == treatment).filter(Appointment.checkin == True);
				import datetime
				today = datetime.datetime.now().date();
				for appt in appts:
					print appt.date
					print today
					days_since = (today - appt.date.date()).days;
					print "days_since: " + str(days_since)
					if int(days_since) in messages:
						patient = Patient.query.filter(Patient.id == appt.user_id).first();
						message = messages[int(days_since)];
						send_message(message, patient.phone_number)
	except ValueError, e:
		return str(e);

def create_fake_appointments():
	pass

def send_merida_reminders():
	try:
		treatment_messages = open('merida_mensajes.txt', 'r');
		messages = {}
		treatment = ""
		for line in treatment_messages:
			if is_number(line) == True:
				messages[int(line)] = next(treatment_messages)
	
		radiation_messages = {'0':[11,14,20], '1':[15,21,23], '2' : [16, 18, 23], '3' : [17,21], '4' : [24, 14, 23], '5' : [18,20], '6':[21,23]}
		chemo_messages = {'0':[29,25], '1':[34, 27, 26], '2':[30,28], '3':[31,32], '4':[33,26], '5':[28], '6':[32]}
		pall_messages = {'0': [35,36], '1':[36], '2':[36,37], '3':[36], '4':[36,38], '5':[36], '6':[36]}
		follow_messages = {'0':[40,41],'1':[], '2':[39], '3':[], '4':[], '5':[], '6':[]}
		monthly = [29, 34, 40]
		rad_pts = Patient.query.filter(Appointment.appt_type == 'MERIDA RADIOTERAPIA');
		chemo_pts = Patient.query.filter(Appointment.appt_type == 'MERIDA QUIMOTERAPIA');
		pall_pts = Patient.query.filter(Appointment.appt_type == 'MERIDA CUIDADOS PALEATIVOS');
		follow_pts = Patient.query.filter(Appointment.appt_type == 'MERIDA SEGUIMIENTO');
		
		import datetime
		from random import randint
		today = str(datetime.datetime.today().weekday())
		for pt in rad_pts:
			for val in radiation_messages[today]:
				send_message(messages[val], pt.phone_number);
				send_message(messages[val], pt.contact_number);
		for pt in chemo_pts:
			for val in chemo_messages[today]:
				if val in monthly:
					if datetime.datetime.today().day < 7:
						send_message(messages[val], pt.phone_number);
						send_message(messages[val], pt.contact_number);		
				else:
					send_message(messages[val], pt.phone_number);
					send_message(messages[val], pt.contact_number);		
		for pt in pall_pts:
			for val in pall_messages[today]:
				if val in monthly:
					if datetime.datetime.today().day < 7:
						send_message(messages[val], pt.phone_number);
						send_message(messages[val], pt.contact_number);		
				else:
					send_message(messages[val], pt.phone_number);
					send_message(messages[val], pt.contact_number);		
		for pt in follow_pts:
			for val in follow_messages[today]:
				if val in monthly:
					if datetime.datetime.today().day < 7:
						send_message(messages[val], pt.phone_number);
						send_message(messages[val], pt.contact_number);		
				else:
					send_message(messages[val], pt.phone_number);
					send_message(messages[val], pt.contact_number);		
			
	except ValueError, e:
		print str(e)
		return str(e)

#create_fake_appointments()

send_appointment_reminders_no_authentication()
send_hemeonc_reminders()
send_diabetes_reminders()
send_merida_reminders()

# send_message('test3 - Speranza Health', '0050250005833')
# dr valvert's 00 502 5050 32 32
# 1150250005833
# 011 502
