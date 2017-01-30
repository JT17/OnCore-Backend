"""Schema for all of Speranza"""

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from datetime import timedelta, datetime

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
        timestamp = (self.date - datetime(1970, 1, 1)).total_seconds()
        patient = Patient.query.filter(Patient.id == self.patient_id).first()
        if patient is None:
            return None
        else:
            patient_name = patient.firstname + " " + patient.lastname
            return {
                'id': self.id,
                'patient_id': self.patient_id,
                'date': timestamp,
                'appt_type': self.appt_type,
                'checkin': self.checkin,
                'checkout': self.checkout,
                'patient_name':patient_name
            }



class Patient(db.Model):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    phone_number = Column(String(250), nullable=False)
    contact_number = Column(String(250), nullable=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True)
    dob = Column(String(250), nullable=False)
    gov_id = Column(Integer, nullable=False)
    text_regimen_id = Column(Integer, ForeignKey('text_regimens.id'), nullable=True)
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
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone_number': self.phone_number,
            'dob': self.dob,
            'gov_id': self.gov_id,
            'regimen_id':self.text_regimen_id
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
    username = db.Column(String(250), nullable=False)
    phone_number = db.Column(String(128), nullable=False)
    email = db.Column(String(250), nullable=False)
    password = db.Column(String(128))
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False)
    pending_access = db.Column(db.Boolean, nullable=False)

    def __init__(self, firstname, lastname, username, phone_number, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.phone_number = phone_number
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.org_id = None
        self.is_admin = False
        self.pending_access = False

    # To add a manager to an org, they first have to have access.
    # They have access when they've already been added to the org which is done by the link
    def set_org(self, org_id):
        org = Organization.query.filter(Organization.id == org_id).first()
        if self.org_id is not None or org is None:
            return None

        has_access = False
        for manager in org.managers:
            if manager.id == self.id:
                has_access = True
                break

        if not has_access:
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
    org_email = Column(String(250), nullable=True)
    managers = db.relationship('Manager', secondary=manager_organization_table)
    admins = db.relationship('Manager', secondary=admin_table)

    def __init__(self, org_name, org_pwd, org_email=None):
        self.org_name = org_name
        if org_email is not None:
            self.org_email = org_email

    @property
    def serialize(self):
        return dict(id=self.id, org_name=self.org_name, org_email=self.org_email,
                    admins=[admin.id for admin in self.admins])

    def add_manager(self, mgr_id):
        for manager in self.managers:
            if manager.id == mgr_id:
                return None
        mgr = Manager.query.filter(Manager.id == mgr_id).first()
        if mgr is None:
            return None
        self.managers.append(mgr)
        return self

    def add_admin(self, mgr_id):
        for admin in self.admins:
            if admin.id == mgr_id:
                return None

        mgr = Manager.query.filter(Manager.id == mgr_id).first()
        if mgr is None:
            return None
        self.admins.append(mgr)
        return self

class Text(db.Model):
    __tablename__ = 'texts'

    id = Column(Integer, primary_key=True)
    org_id = Column(db.Integer, db.ForeignKey('organizations.id'))
    text_msg = Column(String(400), nullable=False)

    def __init__(self, org_id, text_msg):
        self.org_id = org_id
        self.text_msg = text_msg

    @property
    def serialize(self):
        return dict(id=self.id, org_id=self.org_id, text_msg=self.text_msg)

class TextRegimen(db.Model):
    __tablename__ = 'text_regimens'

    id = Column(Integer, primary_key=True)
    org_id = Column(db.Integer, db.ForeignKey('organizations.id'))
    regimen_name=Column(String(250), nullable=False)
    monday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    tuesday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    wednesday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    thursday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    friday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    saturday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)
    sunday_text = Column(db.Integer, db.ForeignKey("texts.id"), nullable=True)

    def __init__(self, org_id, regimen_name, mon_text=None, tue_text=None, wed_text=None, thur_text=None,
                 fri_text=None, sat_text=None, sun_text=None):

        self.org_id = org_id
        self.regimen_name = regimen_name
        self.monday_text = mon_text
        self.tuesday_text = tue_text
        self.wednesday_text = wed_text
        self.thursday_text = thur_text
        self.friday_text = fri_text
        self.saturday_text = sat_text
        self.sunday_text = sun_text

    def add_text(self, msg_id, day):
        day = day.lower()
        if day == 'monday':
            self.monday_text = msg_id
        elif day == 'tuesday':
            self.tuesday_text = msg_id
        elif day == 'wednesday':
            self.wednesday_text = msg_id
        elif day == 'thursday':
            self.thursday_text = msg_id
        elif day == 'friday':
            self.friday_text = msg_id
        elif day == 'saturday':
            self.saturday_text = msg_id
        elif day == 'sunday':
            self.sunday_text = msg_id
        else:
            return -1
        db.session.commit()
        return 1

    def get_texts(self):
        texts = {}
        if(self.monday_text is not None):
            mon_text = Text.query.filter(Text.id == self.monday_text).first()
            texts['monday'] = mon_text.text_msg
        if(self.tuesday_text is not None):
            tue_text = Text.query.filter(Text.id == self.tuesday_text).first()
            texts['tuesday'] = tue_text.text_msg
        if(self.wednesday_text is not None):
            wed_text = Text.query.filter(Text.id == self.wednesday_text).first()
            texts['wednesday'] = wed_text.text_msg
        if(self.thursday_text is not None):
            thur_text = Text.query.filter(Text.id == self.thursday_text).first()
            texts['thursday'] = thur_text.text_msg
        if (self.friday_text is not None):
            fri_text = Text.query.filter(Text.id == self.friday_text).first()
            texts['friday'] = fri_text.text_msg
        if (self.saturday_text is not None):
            sat_text = Text.query.filter(Text.id == self.saturday_text).first()
            texts['friday'] = sat_text.text_msg
        if (self.sunday_text is not None):
            sun_text = Text.query.filter(Text.id == self.sunday_text).first()
            texts['friday'] = sun_text.text_msg
        return texts

    @property
    def serialize(self):
        dict = {}
        dict['id'] = self.id
        dict['org_id'] = self.org_id
        dict['regimen_name'] = self.regimen_name
        if(self.monday_text is not None):
            text = Text.query.filter(Text.id == self.monday_text).first()
            dict['monday_text'] = text.text_msg
        if(self.tuesday_text is not None):
            text = Text.query.filter(Text.id == self.tuesday_text).first()
            dict['tuesday_text'] = text.text_msg
        if (self.wednesday_text is not None):
            text = Text.query.filter(Text.id == self.wednesday_text).first()
            dict['wednesday_text'] = text.text_msg
        if(self.thursday_text is not None):
            text = Text.query.filter(Text.id == self.thursday_text).first()
            dict['thursday_text'] = text.text_msg
        if(self.friday_text is not None):
            text = Text.query.filter(Text.id == self.friday_text).first()
            dict['friday_text'] = text.text_msg
        if(self.saturday_text is not None):
            text = Text.query.filter(Text.id == self.saturday_text).first()
            dict['saturday_text'] = text.text_msg
        if(self.sunday_text is not None):
            text = Text.query.filter(Text.id == self.sunday_text).first()
            dict['sunday_text'] = text.text_msg
        return dict



