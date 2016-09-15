"""Schema for all of Speranza"""

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from speranza.application import application, db

admin_table = db.Table('admin_table',
                       db.Column('manager_id', db.Integer, db.ForeignKey('managers.id'), nullable=False),
                       db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'), nullable=False),
                       db.PrimaryKeyConstraint('manager_id', 'org_id'))

manager_organization_table = db.Table('manager_organization_table',
                                      db.Column('manager_id', db.Integer, db.ForeignKey('managers.id'), nullable=False),
                                      db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('manager_id', 'org_id'))

patient_organization_table = db.Table('patient_organization_table',
                                      db.Column('patient_id', db.Integer, db.ForeignKey('patients.id'), nullable=False),
                                      db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('patient_id', 'org_id'))


class Address(db.Model):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    street_num = Column(Integer, nullable=True)
    street_name = Column(String(250), nullable=True)
    street_type = Column(String(250), nullable=True)
    city_name = Column(String(250), nullable=True)
    zipcode = Column(Integer, nullable=True)
    district = Column(String(250), nullable=True)

    def __init__(self, street_number=None, street_name=None, street_type=None, city_name=None,
                 zipcode=None, district=None):
        self.street_num = street_number
        self.street_name = street_name
        self.street_type = street_type
        self.city_name = city_name
        self.zipcode = zipcode
        self.district = district


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=True)
    date = Column(DateTime, nullable=False)
    appt_type = Column(String(250), nullable=False)
    checkin = Column(Boolean, nullable=False)
    checkout = Column(Boolean, nullable=False)

    def __init__(self, patient_id, manager_id, date, appt_type):
        self.patient_id = patient_id
        self.manager_id = manager_id
        self.date = date
        self.appt_type = appt_type
        self.checkin = False
        self.checkout = False

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date,
            'appt_type': self.appt_type,
            'checkin': self.checkin,
            'checkout': self.checkout
        }

    def __repr__(self):
        return '<User %r>' % self.user_id


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
    @property
    def serialize(self):
        """Return Patient in easily serializable format"""
        return {
            'id':self.id,
            'firstname':self.firstname,
            'lastname':self.lastname,
            'phone_number':self.phone_number,
            'dob':self.dob,
            'gov_id':self.gov_id
        }
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


class Manager(db.Model):
    __tablename__ = 'managers'

    id = db.Column(Integer, primary_key=True)
    firstname = db.Column(String(250), nullable=False)
    lastname = db.Column(String(250), nullable=False)
    phone_number = db.Column(Integer, nullable=False)
    email = db.Column(String(250), nullable=False)
    password = db.Column(String(128))
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    def __init__(self, firstname, lastname, phone_number, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.phone_number = phone_number
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.org_id = -1

    def set_org(self, org_id):
        org = Organization.query.filter(Organization.id == org_id).first()
        if self.org_id != -1 or org is None:
            return None
        self.org_id = org_id
        return self

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=6000):
        s = Serializer(application.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(application.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = Manager.query.get(data['id'])
        return user


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True)
    org_name = Column(String(250), nullable=False)
    org_pwd = Column(String(250), nullable=True)
    org_email = Column(String(250), nullable=True)
    admins = db.relationship('Manager', secondary=admin_table)

    def __init__(self, org_name, org_pwd, org_email=None):
        self.org_name = org_name
        self.org_pwd = org_pwd
        if org_email is not None:
            self.org_email = org_email

    def add_admin(self, mgr_id):
        for admin in self.admins:
            if admin.id == mgr_id:
                return None

        mgr = Manager.query.filter(Manager.id == mgr_id).first()
        if mgr is None:
            return None
        self.admins.append(mgr)
        return self
