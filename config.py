import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))


TOKEN_UKR_NET = os.getenv('TOKEN_UKR_NET')
USER_UKR_NET = os.getenv('USER_UKR_NET')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.ukr.net')
