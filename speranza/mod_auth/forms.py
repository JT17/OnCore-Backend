from flask_wtf import Form
from wtforms import PasswordField, StringField, validators
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    email = StringField('Email Address', [Email(), DataRequired(message='Forgot your email address?')])
    password = PasswordField('Password', [DataRequired(message='Must provide a password. -)')])


class EnterAppointmentInfo(Form):
    appointmentInfo = StringField(label='Appointment to add to DB',
                                  description="db_enter_appointment",
                                  validators=[validators.required(),
                                              validators.Length(min=0, max=128,
                                                                message=u'Enter 128 characters or less')])


class EnterPatientInfo(Form):
    patientInfo = StringField(label='Patient to add to DB', description="db_enter_patient",
                              validators=[validators.required(),
                                          validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])


class RetrieveDBInfo(Form):
    numRetrieve = StringField(label='Number of DB Items to Get',
                              description="db_get",
                              validators=[validators.required(),
                                          validators.Regexp('^\d{1}$', message=u'Enter a number between 1 and 10')])
