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
			#	send_message(message, patient.phone_number);
	except ValueError:
		return str("Couldn't fetch your appointments something went wrong :(");

def send_diabetes_reminders():
	try:
		db_pt_noinsulin = Appointment.query.filter(Appointment.appt_type == 'db_noinsulin');
		for appt in db_pt_noinsulin:
			patient = Patient.query.filter(Patient.id == appt.user_id).first()
			message = "Hi {0}, \n no olvide que necesita comer frutas y vegetables cada dia!".format(patient.firstname)
#			send_message(message, patient.phone_number);
		db_pt_insulin = Appointment.query.filter(Appointment.appt_type == 'db_insulin');
		for appt in db_pt_insulin:
			patient = Patient.query.filter(Patient.id == appt.user_id).first();
			message = "Hi {0}, \n no ovlide que necesita tomer su insulin hoy!".format(patient.firstname)
#			send_message(message, patient.phone_number);

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
#						send_message(message, patient.phone_number)
	except ValueError, e:
		return str(e);

def create_fake_appointments():
	pass

#create_fake_appointments()
#send_appointment_reminders_no_authentication()
#send_hemeonc_reminders();
#send_diabetes_reminders()
send_message('plivo test', '+0050250503232')
