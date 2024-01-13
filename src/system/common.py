import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from flask import session as flask_session
from functools import wraps
from flask import  redirect, url_for, flash

def send_email(recipient: str, 
                               header: str,
                               content: str
                               ):
    # Set up the SMTP server
    s = smtplib.SMTP_SSL(host='mail.hachiba.com.vn', port=465)
    s.login('vuthanh.hoa@hachiba.com.vn', 'Ho*!!811th')

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = 'vuthanh.hoa@hachiba.com.vn'
    msg['To'] = recipient

    # Format the date
    msg['Subject'] = Header(header)
    msg.attach(MIMEText(content, 'plain'))

    # Send the email
    s.send_message(msg)
    s.quit()

#Role setting function
def required_roles(*roles):
   def wrapper(f):
      @wraps(f)
      def wrapped(*args, **kwargs):
         if not set(flask_session["role"]) & set(roles):
            flash('Authentication error, please check your details and try again','error')
            return redirect(url_for('login'))
         return f(*args, **kwargs)
      return wrapped
   return wrapper
