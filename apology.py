from application.models import *
import datetime
import requests
from messenger import send_message

def send_apologies():
	try:
		with open('apology_numbers.txt') as f:
			numbers = set(f.readlines())
			print len(numbers)
			for num in numbers:
				print num
				message = "Hola. Los sentimos para enviarse los mensajes anteayer. Fue un error, y puede ignorarlos. Los sientos!"
				# send_message(message, num);
	except ValueError, e:
		return str(e);

def is_number(s):
	try:
		float(s)
		return True;
	except ValueError:
		return False

send_apologies()
