"""Schema for Organizations"""

from sqlalchemy import Column, Integer, String

from speranza import db
from speranza.mod_managers.models import Manager

admin_table = db.Table('admin_table',
                       db.Column('manager_id', db.Integer, db.ForeignKey('managers.id'), nullable=False),
                       db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'), nullable=False),
                       db.PrimaryKeyConstraint('manager_id', 'org_id'))


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
