from flask import Flask
from passlib.apps import custom_app_context as pwd_context
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from __init__ import db

class Appointment(db.Model):
	__tablename__ = 'appointments'
	id = Column(Integer, primary_key=True)
	user_id= Column(String(80),ForeignKey('users.id'))
	date = Column(DateTime, nullable=False)

	def __init__(self, user_id, date):
		self.user_id = user_id 
		self.date = date 

	def serialize(self):
		"""Return object data in easily serializable format"""
		return{
			'id':self.id,
			'user_id':self.user_id,
			'date':self.date
		}
	def __repr__(self):
		return '<User %r>' % self.user_id

class User(db.Model):
	__tablename__ = 'users'
	
	#user_id is going to be id, so we assign this based on nfc
	id = Column(Integer, primary_key=True)
	firstname = Column(String(250), nullable=False);
	lastname = Column(String(250), nullable=False);
	phone_number = Column(Integer, nullable=False);
	contact_number = Column(Integer, nullable=False);
	address_id = Column(Integer, ForeignKey('addresses.id'));
	type = Column(String(50))
	
	__mapper_args__ = {
		'polymorphic_identity':'user',
		'polymorphic_on':type
	}

	def __init__(self, firstname, lastname, phone_number, contact_number,
			address_id):
		self.firstname = firstname;
		self.lastname = lastname;
		self.phone_number = phone_number;
		self.contact_number = contact_number;
		self.address_id = address_id;
	
	def generate_auth_token(self, expiration=6000):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration);
		return s.dumps({'id':self.id})
	
	@staticmethod
	def verify_auth_token(token):
		s = Serializer(application.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
		 	return None
		user = User.query.get(data['id']);
		return user;	

class Manager(User):
	__tablename__ = 'managers'

	id = Column(Integer, ForeignKey('users.id'), primary_key=True)
	password = Column(String(128))
	__mapper_args__ = {
		'polymorphic_identity':'manager',
	}
	def __init__(self, password):
		self.password = pwd_context.encrypt(password) 
	
	def verify_password(self, password):
		return pwd_context.verify(password, self.password);

class Patient(User):
	__tablename__ = 'patients'

	id = Column(Integer, ForeignKey('users.id'), primary_key = True)
	manager_id = Column(Integer, ForeignKey('manager.id'))

	__mapper_args__ = {
		'polymorphic_identity':'patient',
	}

	def __init__(self, manager_id):
		self.manager_id = manager_id
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
	
