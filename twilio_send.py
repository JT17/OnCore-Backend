from twilio.rest import TwilioRestClient 
 
# put your own credentials here 
ACCOUNT_SID = "AC67374f743c7b1e1625827c13822f5f2b" 
AUTH_TOKEN = "b1a10dd37717ed58a50664a27e9a71c5" 
 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
 
client.messages.create(
	to="5132629488", 
	from_="+15138132587", 
	body="Twilio Test",  
)