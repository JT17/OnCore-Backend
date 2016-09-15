from flask import Flask
from werkzeug.exceptions import *
import unittest
import time
import datetime
import traceback

import speranza.models as models
import speranza.api.addresses
import speranza.api.appointments
import speranza.api.auth
import speranza.api.common
import speranza.api.managers
import speranza.api.patients
import speranza.api.verification
from speranza.application import db


# use this class whenever requests have to be passed into an argument
class Placeholder(object):
    pass


class MyDict(dict):

    def get_json(self):
        print self
        return self


class TestApi(unittest.TestCase):
    def setUp(self):
        self.application = Flask(__name__)

        self.application.config['TESTING'] = True
        self.application.config['WTF_CSRF_ENABLED'] = False
        self.application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.application = self.application.test_client()

        db.create_all()

        self.addr1 = models.Address(city_name="Palo Alto")
        self.addr2 = models.Address(street_number=1234, street_name="test street", street_type="st",
                                    city_name="Palo Alto",
                                    zipcode=98505, district="CA")
        self.addr3 = models.Address(street_number=1234, street_name="test street", street_type="st",
                                    city_name="Palo Alto",
                                    zipcode=98505, district="CA")

        db.session.add(self.addr1)
        db.session.add(self.addr2)
        db.session.add(self.addr3)
        db.session.commit()

        self.org1 = models.Organization(org_name="test_org1", org_pwd="pwd")
        self.org2 = models.Organization(org_name="test_org2", org_pwd="pwd")
        db.session.add(self.org1)
        db.session.add(self.org2)
        db.session.commit()

        self.mgr = models.Manager("test", "mgr", 12345, "abc@abc.com", "pwd")
        self.mgr1 = models.Manager("test", "mgr1", 12345, "blah@abc.com", "pwd")
        self.mgr.set_org(self.org1.id)
        self.mgr1.set_org(self.org2.id)
        db.session.add(self.mgr)
        db.session.add(self.mgr1)
        db.session.commit()

        self.pt1 = models.Patient(firstname="test", lastname="pt1", phone_number=12345,
                                  contact_number=54321, address_id=self.addr1.id, dob="01/01/2000", gov_id=1)
        self.pt2 = models.Patient(firstname="test1", lastname="pt2", phone_number=22222,
                                  contact_number=54321, address_id=self.addr2.id, dob="02/02/2002", gov_id=2)

        self.pt3 = models.Patient(firstname="test2", lastname="pt3", phone_number=33333,
                                  contact_number=54321, address_id=self.addr3.id, dob="03/03/3003", gov_id=3)
        db.session.add(self.pt1)
        db.session.add(self.pt2)
        db.session.add(self.pt3)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.application = None
        self.addr1 = None
        self.addr2 = None
        self.addr3 = None
        self.org1 = None
        self.org2 = None
        self.mgr = None
        self.mgr1 = None
        self.pt1 = None
        self.pt2 = None
        self.pt3 = None

    def test_verify_manager_access(self):
        auth = Placeholder()
        auth.username = self.mgr1.id
        assert not speranza.api.verification.verify_manager_access(self.pt1.id, auth)

        auth.username = self.mgr.id
        assert not speranza.api.verification.verify_manager_access(self.pt1.id, auth)

        self.pt1.add_to_org(self.mgr.org_id)
        assert speranza.api.verification.verify_manager_access(self.pt1.id, auth)
        self.mgr1.org_id = self.org1.id
        assert (self.mgr1.org_id == self.org1.id)
        auth.username = self.mgr1.id
        assert speranza.api.verification.verify_manager_access(self.pt1.id, auth)

    def test_add_appt(self):
        auth = Placeholder()
        auth.username = self.mgr.id
        today = time.time()
        today_ts = datetime.datetime.utcfromtimestamp(int(today))
        self.pt1.add_to_org(self.mgr.org_id)
        request = MyDict()
        request['user_id'] = self.pt1.id
        request['appt_type'] = 'blah'
        request['date'] = today
        request.authorization = auth

        speranza.api.appointments.add_appt(request)
        appts = models.Appointment.query.all()
        assert (len(appts) == 1)
        assert (appts[0].patient_id == self.pt1.id)
        assert (appts[0].appt_type == 'blah')
        assert (appts[0].date == today_ts)

        failed = False
        try:
            speranza.api.appointments.add_appt(request)
        except Exception as e:
            print e
            failed = True
        assert failed
        assert len(models.Appointment.query.all()) == 1

        failed = False
        try:
            auth.username = self.mgr1.id
            request.authorization = auth
            speranza.api.appointments.add_appt(request)
        except Unauthorized as e:
            print e
            failed = True
        assert failed
        assert len(models.Appointment.query.all()) == 1

    def test_checkin_out(self):
        auth = Placeholder()
        auth.username = self.mgr.id
        today = time.time()
        self.pt1.add_to_org(self.mgr.org_id)
        today_ts = datetime.datetime.utcfromtimestamp(float(today))
        appt = models.Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")

        db.session.add(appt)
        db.session.commit()

        request = MyDict()
        request['user_id'] = self.pt1.id
        request['date'] = today
        request.authorization = auth

        speranza.api.appointments.checkin_out(request)
        appts = models.Appointment.query.all()
        assert appts[0].checkin

        failed = False
        try:
            speranza.api.appointments.checkin_out(request)
        except Exception as e:
            assert (type(e) == UnprocessableEntity)
            failed = True
        assert failed
        assert not appts[0].checkout

        speranza.api.appointments.checkin_out(request, checkin=False)
        appts = models.Appointment.query.all()
        assert appts[0].checkout
        failed = False
        try:
            speranza.api.appointments.checkin_out(request, checkin=False)
        except Exception as e:
            assert (type(e) == UnprocessableEntity)
            failed = True
        assert failed

    def test_add_address(self):
        request = MyDict()

        request['street_num'] = 1
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.street_num == 1).all()) == 1

        request['street_name'] = "Test"
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.street_name == "Test").all()) == 1

        request['street_type'] = "St"
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.street_type == "St").all()) == 1

        request['city_name'] = "Cincinnati"
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.city_name == "Cincinnati").all()) == 1

        request['zipcode'] = 12345
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.zipcode == 12345).all()) == 1

        request['district'] = 54321
        speranza.api.addresses.add_address(request)
        assert len(models.Address.query.filter(models.Address.district == 54321).all()) == 1

        assert len(models.Address.query.all()) == 9

    def test_add_patient(self):
        request = MyDict()
        auth = Placeholder()
        auth.username = self.mgr.id
        request.authorization = auth
        failed = False
        try:
            speranza.api.patients.add_patient(request)
        except Exception as e:
            assert (type(e) == UnprocessableEntity), traceback.format_exc()
            failed = True
        assert failed
        request['firstname'] = ""  # Zero length string on purpose to throw exception
        request['lastname'] = "Test"
        request['phone_number'] = "12345678"
        request['contact_number'] = "87654321"
        request['dob'] = 01 / 01 / 2001
        request['gov_id'] = 42
        request['city_name'] = "City"
        failed = False
        try:
            speranza.api.patients.add_patient(request)
        except Exception as e:
            assert (type(e) == UnprocessableEntity), e
            failed = True
        assert failed

        request['firstname'] = "John"
        res = speranza.api.patients.add_patient(request)
        assert (res['patient_contact_number'] == 50287654321), res
        assert len(models.Patient.query.all()) == 4

        # make sure patient is in the right org
        failed = True
        pts = models.Organization.query.filter(models.Organization.id == self.org1.id).first().patients
        for pt in pts:
            if pt.id == res['patient_id']:
                failed = False
                break

        assert not failed

    def test_add_manager(self):
        request = MyDict()
        request['firstname'] = "Test"
        request['lastname'] = "Manager"
        request['email'] = "test@mail.com"
        request['password'] = "password"
        request['phone_number'] = "12345567"

        res = speranza.api.managers.add_manager(request)
        assert (res['msg'] == "success")

        mgr = models.Manager.query.filter(models.Manager.id == res['mgr_id'])
        assert mgr is not None
        assert len(mgr.all()) == 1, len(mgr.all())
        assert mgr.first().firstname == "Test"
        assert mgr.first().verify_password("password")

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
        request = MyDict()
        request.authorization = auth

        appts_res = speranza.api.appointments.get_patient_appts(request)
        assert len(appts_res['appts']) == 0

        appt1 = models.Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
        appt2 = models.Appointment(self.pt2.id, self.mgr.id, today2_ts, "blah")
        appt3 = models.Appointment(self.pt3.id, self.mgr.id, today3_ts, "blah")
        db.session.add(appt1)
        db.session.add(appt2)
        db.session.add(appt3)
        db.session.commit()

        appts_res = speranza.api.appointments.get_patient_appts(request)
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
        request = MyDict()
        request.authorization = auth
        request['user_id'] = self.pt1.id
        res = speranza.api.patients.edit_patient(request)
        assert (res['msg'] == 'success')

        request['phone_number'] = '42'
        speranza.api.patients.edit_patient(request)
        pt = models.Patient.query.filter(models.Patient.id == self.pt1.id).first()
        assert (pt.phone_number == 42)
        failed = False
        try:
            request['phone_number'] = 'a'
            speranza.api.patients.edit_patient(request)
        except Exception as e:
            assert (type(e) == UnprocessableEntity), e
            failed = True
        assert failed
        request['phone_number'] = '42'
        request['contact_number'] = '23'
        speranza.api.patients.edit_patient(request)
        pt = models.Patient.query.filter(models.Patient.id == self.pt1.id).first()
        assert (pt.contact_number == 23)
        request['dob'] = '07/07/07'
        speranza.api.patients.edit_patient(request)
        pt = models.Patient.query.filter(models.Patient.id == self.pt1.id).first()
        assert (pt.dob == '07/07/07')

    def test_edit_patient_address(self):
        auth = Placeholder()
        auth.username = self.mgr.id

        self.pt1.add_to_org(self.mgr.org_id)
        orig_address = models.Address.query.filter(models.Address.id == self.pt1.address_id).first()
        print orig_address

        request = MyDict()
        request.authorization = auth
        request['user_id'] = self.pt1.id
        request['street_num'] = '1'
        request['street_name'] = 'new'
        request['street_type'] = 'ave'
        request['city_name'] = 'edited'
        request['zipcode'] = '55555'
        request['district'] = 'edited'

        speranza.api.patients.edit_patient_address(request)
        models.Patient.query.filter(models.Patient.id == self.pt1.id).first()
        address = models.Address.query.filter(models.Address.id == self.pt1.address_id).first()
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

        request = MyDict()
        request.authorization = auth

        request['firstname'] = 'notthere'
        request['lastname'] = 'hi'
        request['gov_id'] = 100
        request['dob'] = '99/99/99'

        failed = False
        try:
            speranza.api.patients.find_patient(request)
        except Exception as e:
            assert (type(e) == UnprocessableEntity), e
            failed = True
        assert failed

        request['firstname'] = self.pt1.firstname
        request['lastname'] = self.pt1.lastname
        request['dob'] = self.pt1.dob

        res = speranza.api.patients.find_patient(request)
        assert (res['msg'] == 'success')
        assert (len(res['patients']) == 1)
        assert (res['patients'][0]['id'] == self.pt1.id)

        request = MyDict()
        request.authorization = auth
        request['gov_id'] = self.pt1.gov_id
        res = speranza.api.patients.find_patient(request)
        assert (res['patients'][0]['id'] == self.pt1.id)

        self.pt2.firstname = self.pt1.firstname
        self.pt2.lastname = self.pt1.lastname
        self.pt2.dob = self.pt1.dob

        db.session.commit()

        request['firstname'] = self.pt1.firstname
        request['lastname'] = self.pt1.lastname
        request['dob'] = self.pt1.dob

        res = speranza.api.patients.find_patient(request)
        assert (res['msg'] == 'success')
        assert (len(res['patients']) == 2)
        found1 = False
        found2 = False
        for patient in res['patients']:
            if patient['id'] == self.pt1.id:
                found1 = True
            if patient['id'] == self.pt2.id:
                found2 = True
        assert found1
        assert found2

    def test_edit_appt(self):
        auth = Placeholder()
        auth.username = self.mgr.id

        self.pt1.add_to_org(self.mgr.org_id)
        request = MyDict()
        request.authorization = auth

        self.pt1.add_to_org(self.mgr.org_id)
        today = time.time()
        # new_date = today + 1000
        today_ts = datetime.datetime.utcfromtimestamp(int(today))
        appt = models.Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
        db.session.add(appt)
        db.session.commit()
        new_date = today + 1
        request['old_date'] = today
        request['user_id'] = self.pt1.id
        request['appt_type'] = 'new_type'
        res = speranza.api.appointments.edit_appt(request)
        assert res['msg'] == 'success'
        changed_appt = models.Appointment.query.filter(models.Appointment.patient_id == self.pt1.id).first()
        assert changed_appt.appt_type == 'new_type'

        request['new_date'] = new_date
        request['appt_type'] = 'changed_again'
        speranza.api.appointments.edit_appt(request)
        changed_again = models.Appointment.query.filter(models.Appointment.patient_id == self.pt1.id).first()
        assert (changed_again.appt_type == 'changed_again')
        new_date_ts = datetime.datetime.utcfromtimestamp(int(new_date))
        assert changed_again.date == new_date_ts

    def test_delete_appt(self):
        auth = Placeholder()
        auth.username = self.mgr.id

        self.pt1.add_to_org(self.mgr.org_id)
        request = MyDict()
        request.authorization = auth

        today = time.time()
        today_ts = datetime.datetime.utcfromtimestamp(int(today))
        appt = models.Appointment(self.pt1.id, self.mgr.id, today_ts, "blah")
        db.session.add(appt)
        db.session.commit()

        request['user_id'] = self.pt1.id
        request['date'] = today
        speranza.api.appointments.delete_appt(request)
        appts = models.Appointment.query.filter(models.Appointment.patient_id == self.pt1.id).all()
        assert (len(appts) == 0)

    def test_delete_patient(self):
        auth = Placeholder()
        auth.username = self.mgr.id

        p = self.pt1.add_to_org(self.mgr.org_id)
        print p
        request = MyDict()
        request.authorization = auth
        print request.authorization.username

        request['user_id'] = self.pt1.id
        res = speranza.api.patients.delete_patient(request)
        assert res['msg'] == 'success'
        assert len(models.Patient.query.all()) == 2

        failed = False
        try:
            res = speranza.api.patients.delete_patient(request)
            print res
        except Exception as e:
            assert (type(e) == UnprocessableEntity), e
            failed = True
        assert failed


if __name__ == '__main__':
    unittest.main()
