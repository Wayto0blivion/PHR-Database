from flask_mail import Message
from email_test import mail
from email_test import app as mailapp

msg = Message('test email', sender='phr.database.svr@gmail.com', recipients=['phr.database.svr@gmail.com'])
msg.body = 'This is the plain text body'
msg.html = 'This is the <b>HTML</b> body'

with mailapp.app_context():
    mail.send(msg)
