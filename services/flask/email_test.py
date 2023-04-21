import os
from website import create_app
from flask_mail import Mail

app = create_app()

# Gmail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'phr.database.svr@gmail.com'
app.config['MAIL_PASSWORD'] = 'orgrlaafxxjxwnqd'

# Yahoo settings (denied connection to remote host)
# app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'phr_database_svr@yahoo.com'
# app.config['MAIL_PASSWORD'] = 'sc@ryCave65'


mail = Mail(app)

