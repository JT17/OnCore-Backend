"""Schema for Patients"""

from sqlalchemy import Column, ForeignKey, Integer, String

from speranza import db
from speranza.mod_organizations.models import Organization

patient_organization_table = db.Table('patient_organization_table',
                                      db.Column('patient_id', db.Integer, db.ForeignKey('patients.id'), nullable=False),
                                      db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('patient_id', 'org_id'))


class Patient(db.Model):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    phone_number = Column(Integer, nullable=False)
    contact_number = Column(Integer, nullable=False)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True)
    dob = Column(String(250), nullable=False)
    gov_id = Column(Integer, nullable=False)
    organizations = db.relationship('Organization', secondary=patient_organization_table, backref='patients')

    def __init__(self, firstname, lastname, phone_number, contact_number,
                 address_id, dob, gov_id):
        self.firstname = firstname
        self.lastname = lastname
        self.phone_number = phone_number
        self.contact_number = contact_number
        self.address_id = address_id
        self.dob = dob
        self.gov_id = gov_id

    def add_to_org(self, org_id):
        for org in self.organizations:
            if org.id == org_id:
                return None
        org_to_add = Organization.query.filter(Organization.id == org_id).first()
        if org_to_add is None:
            return None
        self.organizations.append(org_to_add)
        return self

    def grant_access(self, org_id):
        for org in self.organizations:
            if org.id == org_id:
                return True
        return False
