import os
import unittest
import time
import datetime
from application import db, application
from application.models import *

import speranza_api
import requests
from json import JSONEncoder
from werkzeug.exceptions import *
application = Flask(__name__)

#use this class whenever requests have to be passed into an argument
class Placeholder(object):
	pass;

class MyDict(dict):
	pass;

class TestApi(unittest.TestCase):
	def setUp(self):
		speranza_api.DEBUG = True;
		application.config['TESTING'] = True
		application.config['WTF_CSRF_ENABLED'] = False
		application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
		self.application = application.test_client()
		db.create_all()

		self.addr1 = Address(city_name="Palo Alto");
		self.addr2 = Address(street_number=1234, street_name="test street", street_type = "st", city_name = "Palo Alto", zipcode=98505, district="CA")
		db.session.add(self.addr1);
		db.session.add(self.addr2);
		db.session.commit();

		self.org1 = Organization(org_name="test_org1", org_pwd = "pwd")
		self.org2 = Organization(org_name="test_org2", org_pwd = "pwd")
		db.session.add(self.org1)
		db.session.add(self.org2)
		db.session.commit()
		

		self.mgr = Manager("test", "mgr", 12345, "abc@abc.com", "pwd");
		self.mgr1 = Manager("test", "mgr1", 12345, "blah@abc.com", "pwd");
		self.mgr.set_org(self.org1.id)
		self.mgr1.set_org(self.org2.id)
		db.session.add(self.mgr)
		db.session.add(self.mgr1)
		db.session.commit()

		self.pt1 = Patient(firstname="test", lastname="pt", phone_number=12345,
				contact_number=54321, address_id=self.addr1.id, dob="01/01/2000", gov_id=1)
		self.pt2 = Patient(firstname="test", lastname="pt", phone_number=22222,
				contact_number=54321, address_id=self.addr2.id, dob="02/02/2002", gov_id=2)
		
		db.session.add(self.pt1)
		db.session.add(self.pt2)
		db.session.commit()
	def tearDown(self):
		db.session.remove();
		db.drop_all();

	def test_verify_manager_access(self):
		auth = Placeholder() 
		auth.username = self.mgr1.id
		assert(speranza_api.verify_manager_access(self.pt1.id, auth) == False)

		auth.username = self.mgr.id
		assert(speranza_api.verify_manager_access(self.pt1.id, auth) == False)

		self.pt1.add_to_org(self.mgr.org_id)
		assert(speranza_api.verify_manager_access(self.pt1.id, auth) == True)

	def test_add_appt(self):
		auth = Placeholder()
		auth.username = self.mgr.id
		today = time.time(); 
		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request['user_id'] = self.pt1.id;
		request['appt_type'] = 'blah'
		request['date'] = today;
		request.authorization = auth

		speranza_api.add_appt(request)
		appts = Appointment.query.all()
		assert(len(appts) == 1)
		assert(appts[0].patient_id == self.pt1.id)
		assert(appts[0].appt_type == 'blah')
		
		failed = False;
		try:
			speranza_api.add_appt(request)
		except:
			failed = True;
		assert(failed)
		assert(len(Appointment.query.all()) == 1)

		failed = False
		try:
			auth.username = self.mgr1.id
			request.authorization = auth;
			speranza_api.add_appt(request)
		except Unauthorized as e:
			failed = True
		assert(failed)
		assert(len(Appointment.query.all()) == 1)

	def test_checkin_out(self):
		auth = Placeholder()
		auth.username = self.mgr.id
		today = time.time()
		self.pt1.add_to_org(self.mgr.org_id)
		today_ts = datetime.datetime.utcfromtimestamp(float(today))
		appt = Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
		db.session.add(appt)
		db.session.commit()
		
		request = MyDict()
		request['user_id'] = self.pt1.id
		request['date'] = today
		request.authorization = auth

		speranza_api.checkin_out(request)
		appts = Appointment.query.all()
		assert(appts[0].checkin == True)

		failed = False
		try:
			speranza_api.checkin_out(request)
		except Exception as e:
			assert(type(e) == UnprocessableEntity)
			failed = True
		assert(failed)
		assert(appts[0].checkout == False)

		speranza_api.checkin_out(request, checkin=False)
		appts = Appointment.query.all()
		assert(appts[0].checkout == True)
		failed = False
		try:
			speranza_api.checkin_out(request, checkin=False)
		except Exception as e:
			assert(type(e) == UnprocessableEntity)
			failed = True
		assert(failed)
if __name__ == '__main__':
	unittest.main()
