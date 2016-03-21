from flask import Flask, request, redirect, jsonify
import twilio.twiml
import oncore_api

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
	resp = twilio.twiml.Response();
	resp.message("Hello, Mobile Monkey");
	return str(resp)

@app.route('/add_appt', methods=['GET', 'POST'])
def add_appt():
	return oncore_api.add_appt(request);

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
	return oncore_api.add_user(request);

@app.route('/get_user_appts', methods=['GET', 'POST'])
def get_user_appts():
	return oncore_api.get_user_appts(request);
if __name__ == "__main__":
	from database import init_db
	init_db()
	app.run(debug=True);
