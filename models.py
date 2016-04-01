from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from database import Base

class Appointment(Base):
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

class User(Base):
	__table__ = 'users'

	#user_id is going to be id, so we assign this based on nfc
	id = Column(Integer, primary_key=True)
	firstname = Column(String(250), nullable=False);
	lastname = Column(String(250), nullable=False);
	phone_number = Column(Integer, nullable=False);
	contact_number = Column(Integer, nullable=False);
	address_id = Column(Integer, ForeignKey('addresses.id'));
	
	def __init__(self, firstname, lastname, phone_number, contact_number,
			address_id):
		self.firstname = firstname;
		self.lastname = lastname;
		self.phone_number = phone_number;
		self.contact_number = contact_number;
		self.address_id = address_id;
class Manager(User):
	__table__ = 'managers'


class Patient(User):

class Address(Base):
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
	
