'''
Simple Flask application to test deployment to Amazon Web Services
Uses Elastic Beanstalk and RDS

Author: Scott Rodkey - rodkeyscott@gmail.com

Step-by-step tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80
'''

from flask import Flask, render_template, request
from flask.ext.httpauth import HTTPBasicAuth
from application import db
from application.models import *
from application.forms import *

from flask import Flask, request, redirect, jsonify, g
import twilio.twiml
import speranza_api

# Elastic Beanstalk initalization
app = Flask(__name__)
app.debug=True
# change this to your own value
# app.secret_key = 'cC1YCIWOj9GgWspgNEo2'   
app.secret_key = 'asdf'  
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, pwd):
	return speranza_api.verify_password(username_or_token, pwd);

@app.route('/api/token', methods=['GET','POST'])
@auth.login_required
def get_auth_token():
	token = g.manager.generate_auth_token()
	return jsonify({'status':'200', 'token':token.decode('ascii')})

@app.route('/hello_monkey', methods=['GET', 'POST'])
@auth.login_required
def hello_monkey():
    resp = twilio.twiml.Response();
    resp.message("Hello, Mobile Monkey");
    return str(resp)

@app.route('/api/add_appt', methods=['GET', 'POST'])
@auth.login_required
def add_appt():
	res = speranza_api.add_appt(request);
	if (res == "success"):
		return jsonify(status="200", value=str(res))	
	else:
		return jsonify(status="500", value=str(res))

@app.route('/api/add_patient', methods=['GET', 'POST'])
@auth.login_required
def add_patient():
	res = speranza_api.add_patient(request);
    	if (res == "success"):
		return jsonify(status="200",value=str(res))
	else:
		return jsonify(status="500", value=str(res))


@app.route('/api/add_manager', methods=['GET', 'POST'])
def add_manager():
	res = speranza_api.add_manager(request);
	if (res['msg'] == "success"):
		return jsonify(status="200", value = (res['msg']), manager_id = (res['mgr_id']))
	else:
		return jsonify(status="500", value = str(res))

#this is a testing function but should not be exposed to any actual users
#@app.route('/api/get_managers', methods=['GET', 'POST'])
def get_managers():
	mgrs = speranza_api.get_managers(request);
	for val in mgrs:
		print val.id
		print val.password
	return redirect('/');
#also a testing function
#@app.route('/api/get_patients', methods=['GET', 'POST'])
def get_patients():
	pts = speranza_api.get_patients(request);
	for val in pts:
		print val.firstname
		print val.id
		print val.manager_id
	return redirect('/');
@app.route('/api/get_user_appts', methods=['GET', 'POST'])
@auth.login_required
def get_user_appts():
	res = speranza_api.get_user_appts(request);
	if type(res) is str:
		return jsonify(status="500",value = str(res))
	else:
		print type(res)
		return jsonify(status="200", value = [i.serialize() for i in res]);

@app.route("/", methods=['GET', 'POST'])
def index():
    # form1 = EnterAppointmentInfo(request.form) 
    # form2 = RetrieveDBInfo(request.form) 
    
    # if request.method == 'POST': #and form1.validate():

    #     data_entered = Data(notes=form1.dbNotes.data)
    #     try:     
    #         db.session.add(data_entered)
    #         db.session.commit()        
    #         db.session.close()
    #     except:
    #         db.session.rollback()
    #     return render_template('thanks.html', notes=form1.dbNotes.data)
        
    # if request.method == 'POST' and form2.validate():
    #     try:   
    #         num_return = int(form2.numRetrieve.data)
    #         query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
    #         for q in query_db:
    #             print(q.notes)
    #         db.session.close()
    #     except:
    #         db.session.rollback()
    #     return render_template('results.html', results=query_db, num_return=num_return)                
    
    #return render_template('index.html', appointmentForm=form1)
    # try:   
    appts = Appointment.query.order_by(Appointment.id.desc())
    # print appts[0]
    #db.session.close()
    #except:
    #    db.session.rollback()
    #if len(appts) > 0:
    #   print appts[0]
    db.session.rollback()
    return render_template('index.html', appts=appts)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
