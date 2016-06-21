from application.models import *
from flask import Flask, request, redirect, jsonify, g
import speranza_api

SAVE_SET = set()
SAVE_SET.add('16303206319')

def delete_all_non_guatemala_patients():
	patients = Patient.query.all();
	appts = Appointment.query.all();
	print "total appointments: ", len(appts)
	print "total patients: ", len(patients)

	non_guatemalan_patients = []
	non_guatemalan_appts = []
	for pt in patients:
		print pt.phone_number
		if str(pt.phone_number)[0:3] != '502':
			non_guatemalan_patients.append((pt.firstname, pt.phone_number, pt.id))
			for appt in appts:
				if appt.user_id == pt.id:
					non_guatemalan_appts.append(appt.user_id)
					try:
						db.session.delete(appt);
						db.session.commit();
					except ValueError, e:
						print str(e) 

			if str(pt.phone_number) not in SAVE_SET:
				try:
					db.session.delete(pt);
					db.session.commit();
				except ValueError, e:
					print str(e) 
			else:
				SAVE_SET.remove(str(pt.phone_number))		

	print "NON GUATEMALAN PATIENTS", len(non_guatemalan_patients)
	print non_guatemalan_patients
	print "NON GUATEMALAN APPTS", len(non_guatemalan_appts)
	print non_guatemalan_appts

def delete_all_soraya_patients():
	patients = Patient.query.all();
	appts = Appointment.query.all();
	print "total appointments: ", len(appts)
	print "total patients: ", len(patients)

	soraya_patients = []
	soraya_appts = []
	for pt in patients:
		print pt.phone_number
		if str(pt.phone_number).find('5025577') != -1 or str(pt.phone_number).find('5025555') != -1:
			soraya_patients.append((pt.firstname, pt.phone_number, pt.id))
			for appt in appts:
				if appt.user_id == pt.id:
					soraya_appts.append(appt.user_id)
					try:
						db.session.delete(appt);
						db.session.commit();
					except ValueError, e:
						print str(e) 

			if str(pt.phone_number) not in SAVE_SET:
				try:
					db.session.delete(pt);
					db.session.commit();
				except ValueError, e:
					print str(e) 
			else:
				SAVE_SET.remove(str(pt.phone_number))		

	print "SORAYA PATIENTS", len(soraya_patients)
	print soraya_patients
	print "SORAYA APPTS", len(soraya_appts)
	print soraya_appts

# delete_all_non_guatemala_patients()
delete_all_soraya_patients()