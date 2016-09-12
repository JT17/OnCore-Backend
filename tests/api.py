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
		self.addr2 = Address(street_number=1234, street_name="test street", street_type="st", city_name="Palo Alto",
							 zipcode=98505, district="CA")
		self.addr3 = Address(street_number=1234, street_name="test street", street_type="st", city_name="Palo Alto",
							 zipcode=98505, district="CA")
		db.session.add(self.addr1);
		db.session.add(self.addr2);
		db.session.add(self.addr3);
		db.session.commit();

		self.org1 = Organization(org_name="test_org1", org_pwd="pwd")
		self.org2 = Organization(org_name="test_org2", org_pwd="pwd")
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

		self.pt1 = Patient(firstname="test", lastname="pt1", phone_number=12345,
						   contact_number=54321, address_id=self.addr1.id, dob="01/01/2000", gov_id=1)
		self.pt2 = Patient(firstname="test", lastname="pt2", phone_number=22222,
						   contact_number=54321, address_id=self.addr2.id, dob="02/02/2002", gov_id=2)

		self.pt3 = Patient(firstname="test", lastname="pt3", phone_number=33333,
						   contact_number=54321, address_id=self.addr3.id, dob="03/03/3003", gov_id=3)
		db.session.add(self.pt1)
		db.session.add(self.pt2)
		db.session.add(self.pt3)
		db.session.commit()

	def tearDown(self):
		db.session.remove();
		db.drop_all();

	def test_verify_manager_access(self):
		auth = Placeholder()
		auth.username = self.mgr1.id
		assert (speranza_api.verify_manager_access(self.pt1.id, auth) == False)

		auth.username = self.mgr.id
		assert (speranza_api.verify_manager_access(self.pt1.id, auth) == False)

		self.pt1.add_to_org(self.mgr.org_id)
		assert (speranza_api.verify_manager_access(self.pt1.id, auth) == True)
		self.mgr1.org_id = self.org1.id
		assert (self.mgr1.org_id == self.org1.id)
		auth.username = self.mgr1.id
		assert (speranza_api.verify_manager_access(self.pt1.id, auth) == True)

	def test_add_appt(self):
		auth = Placeholder()
		auth.username = self.mgr.id
		today = time.time();
		today_ts = datetime.datetime.utcfromtimestamp(int(today))
		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request['user_id'] = self.pt1.id;
		request['appt_type'] = 'blah'
		request['date'] = today;
		request.authorization = auth

		speranza_api.add_appt(request)
		appts = Appointment.query.all()
		assert (len(appts) == 1)
		assert (appts[0].patient_id == self.pt1.id)
		assert (appts[0].appt_type == 'blah')
		assert (appts[0].date == today_ts)

		failed = False;
		try:
			speranza_api.add_appt(request)
		except:
			failed = True;
		assert (failed)
		assert (len(Appointment.query.all()) == 1)

		failed = False
		try:
			auth.username = self.mgr1.id
			request.authorization = auth;
			speranza_api.add_appt(request)
		except Unauthorized as e:
			failed = True
		assert (failed)
		assert (len(Appointment.query.all()) == 1)

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
		assert (appts[0].checkin == True)

		failed = False
		try:
			speranza_api.checkin_out(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity)
			failed = True
		assert (failed)
		assert (appts[0].checkout == False)

		speranza_api.checkin_out(request, checkin=False)
		appts = Appointment.query.all()
		assert (appts[0].checkout == True)
		failed = False
		try:
			speranza_api.checkin_out(request, checkin=False)
		except Exception as e:
			assert (type(e) == UnprocessableEntity)
			failed = True
		assert (failed)

	def test_add_address(self):
		request = MyDict()
		request['street_num'] = 1;
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.street_num == 1).all()) == 1)
		request['street_name'] = "Test"
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.street_name == "Test").all()) == 1)
		request['street_type'] = "St"
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.street_type == "St").all()) == 1), len(
			Address.query.filter(Address.street_type == "St").all())
		request['city_name'] = "Cincinnati"
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.city_name == "Cincinnati").all()) == 1)
		request['zipcode'] = 12345
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.zipcode == 12345).all()) == 1)
		request['district'] = 54321
		speranza_api.add_address(request)
		assert (len(Address.query.filter(Address.district == 54321).all()) == 1)
		assert (len(Address.query.all()) == 9), len(Address.query.all())

	def test_add_patient(self):
		request = MyDict()
		auth = Placeholder()
		auth.username = self.mgr.id
		request.authorization = auth
		failed = False;
		try:
			speranza_api.add_patient(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity), traceback.format_exc()
			failed = True;
		assert (failed)
		request['firstname'] = ""
		request['lastname'] = "Test"
		request['phone_number'] = '12345678'
		request['contact_number'] = 87654321
		request['dob'] = 01 / 01 / 2001
		request['gov_id'] = 42
		request['city_name'] = "City"
		# check that improper name fails
		failed = False;
		try:
			speranza_api.add_patient(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity), e
			failed = True;
		assert (failed)

		request['firstname'] = "John"
		res = speranza_api.add_patient(request)
		assert (res['patient_contact_number'] == 50287654321), res
		assert (len(Patient.query.all()) == 4)

		# make sure patient is in the right org
		failed = True
		pts = Organization.query.filter(Organization.id == self.org1.id).first().patients
		for pt in pts:
			if pt.id == res['patient_id']:
				failed = False;
				break

		assert (failed == False)

	def test_add_manager(self):
		request = MyDict()
		request['firstname'] = "Test"
		request['lastname'] = "Manager"
		request['email'] = "test@mail.com"
		request['password'] = "password"
		request['phone_number'] = 12345567

		res = speranza_api.add_manager(request)
		assert (res['msg'] == "success")

		mgr = Manager.query.filter(Manager.id == res['mgr_id'])
		assert mgr is not None
		assert len(mgr.all()) == 1, len(mgr.all())
		assert mgr.first().firstname == "Test"
		assert mgr.first().verify_password("password") == True

	def test_get_user_appts(self):
		auth = Placeholder()
		auth.username = self.mgr.id
		minutedelta = datetime.timedelta(minutes=1)

		today_ts = datetime.datetime.now()
		today2_ts = today_ts - minutedelta
		today3_ts = today_ts - minutedelta - minutedelta
		self.pt1.add_to_org(self.mgr.org_id)
		self.pt2.add_to_org(self.mgr.org_id)
		self.pt3.add_to_org(self.mgr.org_id)
		request = MyDict();
		request.authorization = auth

		appts_res = speranza_api.get_user_appts(request)
		assert (len(appts_res['appts']) == 0)

		appt1 = Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
		appt2 = Appointment(self.pt2.id, self.mgr.id, today2_ts, "blah")
		appt3 = Appointment(self.pt3.id, self.mgr.id, today3_ts, "blah")
		db.session.add(appt1)
		db.session.add(appt2)
		db.session.add(appt3)
		db.session.commit()

		appts_res = speranza_api.get_user_appts(request)
		appts = appts_res['appts']
		assert (len(appts) == 3), len(appts)
		appt_by_date = sorted(appts, key=lambda appt: appt['date'])
		assert (appt_by_date[0]['patient_id'] == self.pt3.id)
		assert (appt_by_date[0]['date'] == today3_ts)
		assert (appt_by_date[0]['firstname'] == self.pt3.firstname)
		assert (appt_by_date[0]['lastname'] == self.pt3.lastname)
		assert (appt_by_date[0]['appt_type'] == "blah")
		assert (appt_by_date[2]['patient_id'] == self.pt1.id)
		assert (appt_by_date[2]['date'] == today_ts)
		assert (appt_by_date[2]['firstname'] == self.pt1.firstname)
		assert (appt_by_date[2]['lastname'] == self.pt1.lastname)
		assert (appt_by_date[2]['appt_type'] == "blah")

	def test_edit_patient(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request.authorization = auth
		request['user_id'] = self.pt1.id
		res = speranza_api.edit_patient(request)
		assert (res['msg'] == 'success')

		request['phone_number'] = '42'
		res = speranza_api.edit_patient(request)
		pt = Patient.query.filter(Patient.id == self.pt1.id).first()
		assert (pt.phone_number == 42)
		failed = False;
		try:
			request['phone_number'] = 'a'
			res = speranza_api.edit_patient(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity), e
			failed = True;
		assert (failed == True)
		request['phone_number'] = '42'
		request['contact_number'] = '23'
		res = speranza_api.edit_patient(request)
		pt = Patient.query.filter(Patient.id == self.pt1.id).first()
		assert (pt.contact_number == 23)
		request['dob'] = '07/07/07'
		res = speranza_api.edit_patient(request)
		pt = Patient.query.filter(Patient.id == self.pt1.id).first()
		assert (pt.dob == '07/07/07')

	def test_edit_patient_address(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		orig_address = Address.query.filter(Address.id == self.pt1.address_id).first()
		request = MyDict();
		request.authorization = auth
		request['user_id'] = self.pt1.id
		request['street_num'] = '1'
		request['street_name'] = 'new'
		request['street_type'] = 'ave'
		request['city_name'] = 'edited'
		request['zipcode'] = '55555'
		request['district'] = 'edited'
		speranza_api.edit_patient_address(request)
		pt1 = Patient.query.filter(Patient.id == self.pt1.id).first()
		address = Address.query.filter(Address.id == self.pt1.address_id).first()
		assert (address.street_num == 1)
		assert (address.street_name == 'new')
		assert (address.street_type == 'ave')
		assert (address.city_name == 'edited')
		assert (address.zipcode == 55555)
		assert (address.district == 'edited')

	def test_find_patient(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		self.pt2.add_to_org(self.mgr.org_id)
		self.pt3.add_to_org(self.mgr.org_id)

		request = MyDict();
		request.authorization = auth

		request['firstname'] = 'notthere'
		request['lastname'] = 'hi'
		request['gov_id'] = 100
		request['dob'] = '99/99/99'

		failed = False
		try:
			speranza_api.find_patient(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity), e
			failed = True
		assert (failed)

		request['firstname'] = self.pt1.firstname
		request['lastname'] = self.pt1.lastname
		request['dob'] = self.pt1.dob

		res = speranza_api.find_patient(request)
		assert (res['msg'] == 'success')
		assert (len(res['patients']) == 1)
		assert (res['patients'][0].id == self.pt1.id)

		request = MyDict();
		request.authorization = auth
		request['gov_id'] = self.pt1.gov_id
		res = speranza_api.find_patient(request)
		assert (res['patients'][0].id == self.pt1.id)

		self.pt2.firstname = self.pt1.firstname
		self.pt2.lastname = self.pt1.lastname
		self.pt2.dob = self.pt1.dob

		db.session.commit()

		request['firstname'] = self.pt1.firstname
		request['lastname'] = self.pt1.lastname
		request['dob'] = self.pt1.dob

		res = speranza_api.find_patient(request)
		res = speranza_api.find_patient(request)
		assert (res['msg'] == 'success')
		assert (len(res['patients']) == 2)
		found1 = False
		found2 = False
		for patient in res['patients']:
			if patient.id == self.pt1.id:
				found1 = True
			if patient.id == self.pt2.id:
				found2 = True
		assert (found1)
		assert (found2)

	def test_edit_appt(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request.authorization = auth

		self.pt1.add_to_org(self.mgr.org_id)
		today = time.time()
		new_date = today + 1000
		today_ts = datetime.datetime.utcfromtimestamp(int(today))
		appt = Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
		db.session.add(appt)
		db.session.commit()
		new_date = today + 1
		request['old_date'] = today
		request['user_id'] = self.pt1.id
		request['appt_type'] = 'new_type'
		res = speranza_api.edit_appt(request)
		assert (res['msg'] == 'success')
		changed_appt = Appointment.query.filter(Appointment.patient_id == self.pt1.id).first()
		assert (changed_appt.appt_type == 'new_type')

		request['new_date'] = new_date
		request['appt_type'] = 'changed_again'
		res = speranza_api.edit_appt(request)
		changed_again = Appointment.query.filter(Appointment.patient_id == self.pt1.id).first()
		assert (changed_again.appt_type == 'changed_again')
		new_date_ts = datetime.datetime.utcfromtimestamp(int(new_date))
		assert (changed_again.date == new_date_ts)

	def test_delete_appt(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request.authorization = auth

		today = time.time()
		today_ts = datetime.datetime.utcfromtimestamp(int(today))
		appt = Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
		db.session.add(appt)
		db.session.commit()

		request['user_id'] = self.pt1.id
		request['date'] = today
		res = speranza_api.delete_appt(request)
		appts = Appointment.query.filter(Appointment.patient_id == self.pt1.id).all()
		assert (len(appts) == 0)

	def test_delete_patient(self):
		auth = Placeholder()
		auth.username = self.mgr.id

		self.pt1.add_to_org(self.mgr.org_id)
		request = MyDict();
		request.authorization = auth

		request['user_id'] = self.pt1.id
		res = speranza_api.delete_patient(request)
		assert (res['msg'] == 'success')
		assert (len(Patient.query.all()) == 2)

		failed = False
		try:
			res = speranza_api.delete_patient(request)
		except Exception as e:
			assert (type(e) == UnprocessableEntity), e
			failed = True
		assert (failed)
if __name__ == '__main__':
	unittest.main()
