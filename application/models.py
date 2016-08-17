from flask import Flask
from passlib.apps import custom_app_context as pwd_context
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from __init__ import db, application as app

patient_organization_table = db.Table('patient_organization_table',
					db.Column('patient_id', db.Integer, db.ForeignKey('patients.id'), nullable=False),
					db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'), nullable=False),
					db.PrimaryKeyConstraint('patient_id','org_id'))
class Appointment(db.Model):
	__tablename__ = 'appointments'
	id = Column(Integer, primary_key=True)
	patient_id = Column(Integer,ForeignKey('patients.id'))
	date = Column(DateTime, nullable=False)
	appt_type = Column(String(250), nullable=False);
	checkin = Column(Boolean, nullable = False);
	checkout = Column(Boolean, nullable = False);
	def __init__(self, patient_id, date, appt_type):
		self.patient_id = patient_id 
		self.date = date 
		self.appt_type = appt_type
		self.checkin = False;
		self.checkout = False;
	def serialize(self):
		"""Return object data in easily serializable format"""
		return{
			'id':self.id,
			'patient_id':self.patient_id,
			'date':self.date,
			'appt_type':self.appt_type,
			'checkin':self.checkin,
			'checkout':self.checkout
		}
	def __repr__(self):
		return '<User %r>' % self.user_id


class Manager(db.Model):
	__tablename__ = 'managers'

	id = db.Column(Integer, primary_key=True);
	firstname = db.Column(String(250), nullable=False);
	lastname = db.Column(String(250), nullable=False);
	phone_number = db.Column(Integer, nullable=False);
	email = db.Column(String(250), nullable=False);
	password = db.Column(String(128))
	org_id = db.Column(Integer, ForeignKey('organizations'), nullable=True)
	def __init__(self, firstname, lastname, phone_number, contact_number,
			address_id, password):
		self.firstname = firstname;
		self.lastname = lastname;
		self.phone_number = phone_number;
		self.email = email;
		self.password = pwd_context.encrypt(password) 
		self.org_id = 0;
	
	def verify_password(self, password):
		return pwd_context.verify(password, self.password);

	def generate_auth_token(self, expiration=6000):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration);
		return s.dumps({'id':self.id})
	
	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
		 	return None
		user = Manager.query.get(data['id']);
		return user;	

class Patient(db.Model):
	__tablename__ = 'patients'

	id = Column(Integer, primary_key=True)
	firstname = Column(String(250), nullable=False);
	lastname = Column(String(250), nullable=False);
	phone_number = Column(Integer, nullable=False);
	contact_number = Column(Integer, nullable=False);
	address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True);
	dob = Column(String(250), nullable=False)
	gov_id = Column(Integer, nullable = False)
	def __init__(self, firstname, lastname, phone_number, contact_number,
			address_id, dob, gov_id):
		self.firstname = firstname;
		self.lastname = lastname;
		self.phone_number = phone_number;
		self.contact_number = contact_number;
		self.address_id = address_id;
		self.manager_id = organization_id; 
		self.dob = dob
		self.gov_id = gov_id

class Address(db.Model):
	__tablename__ = 'addresses'

	id = Column(Integer, primary_key=True)
	street_num = Column(Integer, nullable=True);
	street_name = Column(String(250), nullable=True);
	street_type = Column(String(250), nullable=True);
	city_name = Column(String(250), nullable=True);
	zipcode = Column(Integer, nullable=True);
	district = Column(String(250), nullable=True);
	
	def __init__(self, street_number=None, street_name=None, street_type=None, city_name=None, 
			zipcode=None, district=None): 
		self.street_num = street_number;
		self.street_name = street_name;
		self.street_type = street_type;
		self.city_name = city_name;
		self.zipcode = zipcode;
		self.district = district

class Organization(db.Model):
	__tablename__ = 'organizations'

	id = Column(Integer, primary_key=True);
	org_name = Column(String(250), nullable=False);
	org_pwd= Column(String(250), nullable=True);
	admin_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
	org_email = Column(String(250), nullable=True);

	def __init__(self, org_name, org_pwd, admin_id, org_email=None):
		admin = Manager.query.get(admin_id);
		if(admin is None):
			raise ValueError('Admin_id is invalid')
		self.org_name = org_name;
		self.org_pwd = org_pwd;
		self.admin_id = admin_id;
		if(org_email is not None):
			self.org_email = org_email;
