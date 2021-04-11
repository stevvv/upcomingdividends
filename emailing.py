import smtplib, ssl
import os
import base64 as xxx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def my_email(reciever, subject, content):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "email@gmail.com"
    html = content
    #password = xxx.b64decode(os.environ["st_pass"]).decode('utf-8')
    password = str(os.environ["MYVAR"])

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(reciever)
    part1 = MIMEText(html, "html")
    message.attach(part1)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, reciever, message.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 
        #print('done')
