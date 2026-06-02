import os

from dotenv import load_dotenv

load_dotenv()


TOKEN_UKR_NET = os.getenv('TOKEN_UKR_NET')
USER_UKR_NET = os.getenv('USER_UKR_NET')
SMTP_SERVER = os.getenv('SMTP_SERVER')

print(TOKEN_UKR_NET)