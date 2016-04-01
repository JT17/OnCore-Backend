from flask.ext.wtf import Form
from wtforms import TextField, validators

class EnterAppointmentInfo(Form):
    appointmentInfo = TextField(label='Appointment to add to DB', description="db_enter_appointment", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])    

class EnterPatientInfo(Form):
	patientInfo = TextField(label='Patient to add to DB', description="db_enter_patient", validators=[validators.required(), validators.Length(min=0, max=128, message=u'Enter 128 characters or less')])    

class RetrieveDBInfo(Form):
    numRetrieve = TextField(label='Number of DB Items to Get', description="db_get", validators=[validators.required(), validators.Regexp('^\d{1}$',message=u'Enter a number between 1 and 10')])
