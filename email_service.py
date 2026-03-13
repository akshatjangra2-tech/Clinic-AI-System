import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# TEMP TEST EMAIL (LATER CHANGE)
EMAIL_USER = "bindassyaar9@gmail.com"
EMAIL_PASS = "gulaabooo"


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()
