from email import header
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from rsa import verify
from settings import email_login, email_password
from re import *


# самая базовая проверка на то, является ли строка почтой
def is_email(email):
    pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    is_valid = pattern.match(email)
    if is_valid:
        return True
    else:
        return False


# функция отправки сообщения
def send_message(email, message_to_send, subject="Алерт"):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg.attach(MIMEText(message_to_send, 'plain'))
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as server:
        
        server.ehlo()
        server.login(email_login, email_password)
        server.sendmail(email_login, email, msg.as_string())
        server.close()
