"""Schema for Addresses"""

from sqlalchemy import Column, Integer, String
from speranza import db


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
