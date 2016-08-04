from application.models import *
import datetime
import requests
from messenger import send_message

# FRONTLINESMS_API_KEY = "309fefe6-e619-4766-a4a2-53f0891fde23"
# FRONTLINESMS_WEBHOOK = "https://cloud.frontlinesms.com/api/1/webhook"
# -*- coding: utf-8 -*-

def send_apologies():
	try:
		numbers = [FILL IN HERE]	
		for num in numbers:
			print num
			message = "Hola. Los sentimos para enviarse los mensajes anteayer. Fue un error, y puede ignorarlos. Los sientos!"
			send_message(message, num);
	except ValueError, e:
		return str(e);

def is_number(s):
	try:
		float(s)
		return True;
	except ValueError:
		return False

send_apologies()
