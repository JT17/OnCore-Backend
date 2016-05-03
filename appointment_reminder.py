from application.models import *
from flask import Flask, request, redirect, jsonify, g
import datetime
import requests

FRONTLINESMS_API_KEY = "309fefe6-e619-4766-a4a2-53f0891fde23"
FRONTLINESMS_WEBHOOK = "https://cloud.frontlinesms.com/api/1/webhook"

def send_appointment_reminders_no_authentication():
	import json
	try:
		all_appts = Appointment.query.all()
		for appt in all_appts:
			print appt.user_id
			print appt.date
			print datetime.datetime.now() # TODO maybe should be utcnow?
			time_until_appointment = appt.date - datetime.datetime.now()
			print time_until_appointment
		 	if time_until_appointment <= datetime.timedelta(days=1):
		 		patient = Patient.query.filter(Patient.id == appt.user_id).first()
		 		message = "Hi {0}, \n this is a reminder about your appointment scheduled on {1}".format(patient.firstname, str(appt.date))
		 		r = requests.post(FRONTLINESMS_WEBHOOK, json={"apiKey": FRONTLINESMS_API_KEY, 
					"payload":{"message": message, "recipients":[{"type": "mobile", "value": '+'+str(patient.phone_number)}]}});
	except ValueError:
		return str("Couldn't fetch your appointments something went wrong :(");

send_appointment_reminders_no_authentication()