import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN') # token sended by Bot Father

owner = '441260639' # owner id
delay_main_alert_func = 100 # delay between data updates for alerts


email_login = os.getenv('EMAIL_LOGIN') # login of gmail, which sends messages to users
email_password = os.getenv('EMAIL_PASSWORD') # password of gmail, which sends messages to users

