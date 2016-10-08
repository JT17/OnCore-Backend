import smtplib
#TODO: replace with speranza information
SENDER = "jonathan.tiao17@gmail.com"
AUTH = "prtaovmolauyhecy"
SERVER_CONN = "smtp.gmail.com:587"

def login_to_server(server_conn = SERVER_CONN, sender = SENDER, auth = AUTH):
    server = smtplib.SMTP(server_conn)
    server.ehlo()
    server.starttls()
    server.login(sender, auth)
    return server

def create_message(text, subj, dest, src):
    message =  "\r\n".join([ "From: {0}".format(src), "To: {0}".format(dest), "Subject: {0}".format(subj.encode("utf-8")), "", text])
    return message

def send_formatted_email(msg, dest, server):
    try:
        val = server.sendmail(dest, SENDER, msg)
    except smtplib.SMTPRecipientsRefused as e:
        return e.recipients
    except smtplib.SMTPHeloError as e:
        return e.message
    except smtplib.SMTPDataError as e:
        return e.message
    return "success"

def send_email(msg_txt, targets, subj):
    server = login_to_server()
    for target in targets:
        message = create_message(msg_txt, subj, target, SENDER)
        res = send_formatted_email(message, target, server)
        if res is not "success":
            return res
    return "success"