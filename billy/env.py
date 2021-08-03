import os

from dotenv import load_dotenv


def get(name):
    value = os.getenv(name)
    if not value or len(value) == 0:
        raise Exception("missing environment variable: " + name)
    return value


load_dotenv('./env/server.env')

CLIENT_ORIGIN = get('CLIENT_ORIGIN')
REDIRECT_URL_LOGIN = get('REDIRECT_URL_LOGIN')

load_dotenv('./env/hitobito.env')

HITOBITO_LANG = get('HITOBITO_LANG')
HITOBITO_HOST = get('HITOBITO_HOST')
HITOBITO_GROUP = int(get('HITOBITO_GROUP'))

HITOBITO_OAUTH_CLIENT_ID = get('HITOBITO_OAUTH_CLIENT_ID')
HITOBITO_OAUTH_SECRET = get('HITOBITO_OAUTH_SECRET')

HITOBITO_ALLOWED_USERS = get('HITOBITO_ALLOWED_USERS')
HITOBITO_TOKEN_USER = get('HITOBITO_TOKEN_USER')
HITOBITO_TOKEN = get('HITOBITO_TOKEN')

load_dotenv('./env/bank.env')

BANK_REF_PREFIX = get('BANK_REF_PREFIX')
BANK_IBAN = get('BANK_IBAN')

load_dotenv('./env/mail.env')

MAIL_DEFAULT_SENDER = get('MAIL_DEFAULT_SENDER')
