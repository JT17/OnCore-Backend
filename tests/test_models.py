"""
Tests all of the models and join tables
(manager_organization_table and admin_table are tested together in one test)
"""

from flask import Flask
import unittest
import datetime

from speranza.models import Address, Appointment, Manager, Organization, Patient
from speranza.application import db


class TestModels(unittest.TestCase):
    def setUp(self):
        self.application = Flask(__name__)
        self.application.config.from_object('tests.config')

        db.init_app(self.application)
        db.create_all()

        self.application = self.application.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.application = None

    def test_address(self):
        full_address = Address(street_number=1234, street_name="test street", street_type="st", city_name="Palo Alto",
                               zipcode=98505, district="CA")
        only_city = Address(city_name="Palo Alto")
        db.session.add(full_address)
        db.session.add(only_city)
        db.session.commit()
        fetch_city = Address.query.filter(Address.city_name == "Palo Alto").all()
        fetch_full = Address.query.filter(Address.street_num == 1234).all()
        assert (len(fetch_full) == 1)
        assert (len(fetch_city) == 2)

    def test_patient(self):
        pt_address = Address(city_name="Palo Alto")
        pt_org = Organization(org_name="test_org", org_pwd="pwd")

        db.session.add(pt_address)
        db.session.add(pt_org)
        db.session.commit()

        patient = Patient(firstname="test", lastname="pt", phone_number=12345,
                          contact_number=54321, address_id=pt_address.id, dob="01/01/2000", gov_id=1)
        db.session.add(patient)
        db.session.commit()

        f_p = Patient.query.all()
        assert (len(f_p) == 1)

        patient.add_to_org(pt_org.id)
        assert len(patient.organizations) == 1
        assert not patient.grant_access(1000)
        assert patient.grant_access(pt_org.id)

        patient.add_to_org(10000)
        assert len(patient.organizations) == 1

    def test_appointment(self):
        time = datetime.datetime.now()
        new_appointment = Appointment(1, 1, time, "test")
        db.session.add(new_appointment)
        db.session.commit()
        test_fetch = Appointment.query.filter(Appointment.patient_id == 1).filter(Appointment.manager_id == 1).first()
        assert (test_fetch is not None)
        assert (test_fetch.date == time)
        assert (test_fetch.patient_id == 1)

        ser_test = test_fetch.serialize()
        assert (ser_test['patient_id'] == 1)

    def test_manager(self):
        manager = Manager(firstname="test", lastname="user", phone_number=12345, password="pass",
                          email="test_email@email.com")
        assert (manager.org_id == -1)
        db.session.add(manager)
        db.session.commit()
        fetch_mgr = Manager.query.filter(Manager.firstname == "test").filter(Manager.lastname == "user").first()
        assert fetch_mgr is not None
        assert fetch_mgr.verify_password("pass")
        assert fetch_mgr.firstname == "test"

    def test_org(self):
        new_org = Organization(org_name="test", org_pwd="pwd", org_email="test_email")
        db.session.add(new_org)
        db.session.commit()

        f_o = Organization.query.all()
        assert (len(f_o) == 1)

        admin1 = Manager(firstname="admin", lastname="wan", phone_number=12345, password="pass",
                         email="test_email@email.com")
        admin2 = Manager(firstname="admin", lastname="two", phone_number=12345, password="pass",
                         email="test_email@email.com")

        db.session.add(admin1)
        db.session.add(admin2)
        db.session.commit()

        new_org.add_admin(admin1.id)
        assert (len(new_org.admins) == 1)
        new_org.add_admin(admin1.id)
        assert (len(new_org.admins) == 1)

        new_org.add_admin(admin2.id)
        assert (len(new_org.admins) == 2)

        new_org.add_admin(12345)
        assert (len(new_org.admins) == 2)

        print new_org.serialize

        # new_org.patients

    def test_org_pt(self):
        pt_address = Address(city_name="Palo Alto")
        db.session.add(pt_address)
        db.session.commit()
        p1 = Patient(firstname="test", lastname="pt", phone_number=12345,
                     contact_number=54321, address_id=pt_address.id, dob="01/01/2000", gov_id=1)
        p2 = Patient(firstname="test1", lastname="pt", phone_number=12345,
                     contact_number=54321, address_id=pt_address.id, dob="01/01/2000", gov_id=2)
        new_org = Organization(org_name="test", org_pwd="pwd", org_email="test_email")
        second_org = Organization(org_name="test2", org_pwd="pwd", org_email="test_email")
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(new_org)
        db.session.add(second_org)
        db.session.commit()

        p1.add_to_org(new_org.id)
        assert (len(p1.organizations) == 1)

        p1.add_to_org(second_org.id)
        assert (len(p1.organizations) == 2)

        assert (len(new_org.patients) == 1)
        assert (len(second_org.patients) == 1)

        p2.add_to_org(new_org.id)
        assert (len(new_org.patients) == 2)

    def test_org_manager(self):
        mgr = Manager("test", "mgr", 12345, "abc@abc.com", "pwd")
        org = Organization("test", "org")
        db.session.add(org)
        db.session.commit()

        db.session.add(mgr)
        db.session.commit()
        assert (mgr.set_org(org.id) is None)

        org.add_manager(mgr.id)
        assert(mgr.set_org(org.id) is not None)
        assert(mgr.org_id == org.id)
        org.add_admin(mgr.id)

        res = org.add_admin(mgr.id)

        assert (res is None)
        assert (len(org.admins) == 1)
        assert (org.admins[0].id == mgr.id)

        assert (mgr.org_id == org.id)
        assert (mgr.set_org(10) is None)
