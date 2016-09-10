"""Tests for our API implementation"""
import json
import unittest

from speranza import db, application

from speranza.mod_addresses.models import Address
from speranza.mod_managers.models import Manager
from speranza.mod_organizations.models import Organization
from speranza.mod_patients.models import Patient

from speranza.api.managers import verify_manager_access
from speranza.api.appointments import add_appt


# use this class whenever requests have to be passed into an argument
class Placeholder(object):
    pass


class TestApi(unittest.TestCase):
    def setUp(self):
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.application = application.test_client()
        db.create_all()

        self.addr1 = Address(city_name="Palo Alto");
        self.addr2 = Address(street_number=1234, street_name="test street", street_type="st", city_name="Palo Alto",
                             zipcode=98505, district="CA")
        db.session.add(self.addr1);
        db.session.add(self.addr2);
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
        assert (verify_manager_access(self.pt1, auth) == False)

        auth.username = self.mgr.id
        assert (verify_manager_access(self.pt1, auth) == False)

        self.pt1.add_to_org(self.mgr.org_id)
        assert (verify_manager_access(self.pt1, auth) == True)

    def test_add_appt(self):
        auth = Placeholder()
        auth.username = self.mgr1.id
        # speranza_api.DEBUG = True;
        request = json.dumps({'user_id': 1, 'appt_type': "blah", 'date': 1, 'authorization': auth})
        request.authorization = auth
        add_appt(request)


if __name__ == '__main__':
    unittest.main()
