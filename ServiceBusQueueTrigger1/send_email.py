import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
import os


def email_alert(subject, body, pers=False, attachmentpath=False, auditemail=False):
    '''sends an email to cbarry and dbernier. 
    pers = true means email only goes to cbarry
    '''
    SUBJECT = subject
    MY_EMAIL = 'qauser2@darlingconsulting.com'
    MY_PASSWORD = os.environ['startline']
    if pers:
        TO_EMAIL = ['cbarry@darlingconsulting.com']
    elif auditemail:
        TO_EMAIL = ['cbarry@darlingconsulting.com', 'dbernier@darlingconsulting.com', auditemail]
    else:
        TO_EMAIL = ['cbarry@darlingconsulting.com', 'dbernier@darlingconsulting.com']

    SMTP_SERVER = 'smtp.office365.com'
    SMTP_PORT = 587

    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = COMMASPACE.join(TO_EMAIL)
    msg['Subject'] = SUBJECT


    if attachmentpath:
        # open and read the CSV file in binary
        with open(attachmentpath,'rb') as file:
        # Attach the file with filename to the email
            msg.attach(MIMEApplication(file.read(), Name=attachmentpath))


    body = MIMEText(body) # convert the body to a MIME compatible string
    msg.attach(body) # attach it to your main message


    smtpObj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(MY_EMAIL, MY_PASSWORD)
    smtpObj.sendmail(MY_EMAIL, TO_EMAIL, msg.as_string())
    smtpObj.quit()
    return True
