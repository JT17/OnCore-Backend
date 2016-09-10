"""Schema for Managers"""

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Integer, String

from speranza.mod_organizations.models import Organization
from speranza import application, db


manager_organization_table = db.Table('manager_organization_table',
                                      db.Column('manager_id', db.Integer, db.ForeignKey('managers.id'), nullable=False),
                                      db.Column('org_id', db.Integer, db.ForeignKey('organizations.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('manager_id', 'org_id'))


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
