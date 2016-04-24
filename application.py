'''
Simple Flask application to test deployment to Amazon Web Services
Uses Elastic Beanstalk and RDS

Author: Scott Rodkey - rodkeyscott@gmail.com

Step-by-step tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80
'''

from flask import Flask, render_template, request
from application import db
from application.models import *
from application.forms import *

from flask import Flask, request, redirect, jsonify
import twilio.twiml
import speranza_api

# Elastic Beanstalk initalization
app = Flask(__name__)
app.debug=True
# change this to your own value
# app.secret_key = 'cC1YCIWOj9GgWspgNEo2'   
app.secret_key = 'asdf'  

@app.route('/hello_monkey', methods=['GET', 'POST'])
def hello_monkey():
    resp = twilio.twiml.Response();
    resp.message("Hello, Mobile Monkey");
    return str(resp)

@app.route('/add_appt', methods=['GET', 'POST'])
def add_appt():
    print "add_appt"
    speranza_api.add_appt(request);
    return redirect('/');


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    speranza_api.add_user(request);
    return redirect('/');

@app.route('/get_user_appts', methods=['GET', 'POST'])
def get_user_appts():
    speranza_api.get_user_appts(request);
    return redirect('/');

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
