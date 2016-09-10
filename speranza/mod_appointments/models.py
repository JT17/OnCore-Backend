"""Schema for Appointments"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from speranza import db


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
