import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback


class Mail():
    def __init__(self, email, pass_key):
        self.email = email
        self.pass_key = pass_key
        self.mail_port = 587
        self.server = 'smtp.googlemail.com'

    def send_email(self, subject, recipient, message):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = recipient
        msg['Subject'] = subject

        body = message
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.server, self.mail_port)
            server.starttls()
            server.login(self.email, self.pass_key)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            traceback.print_exc()
            print("Failed to send email:", str(e))
