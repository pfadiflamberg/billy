import help
from http import HTTPStatus
from dotenv import load_dotenv
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized

load_dotenv('./env/hitobito.env')
load_dotenv('./env/server.env')

HITOBITO_BASE = help.getenv('HITOBITO_HOST')

dance = OAuth2ConsumerBlueprint(
    "billy", __name__,
    client_id=help.getenv('HITOBITO_OAUTH_CLIENT_ID'),
    client_secret=help.getenv('HITOBITO_OAUTH_SECRET'),
    base_url=HITOBITO_BASE,
    token_url="{base}/oauth/token".format(base=HITOBITO_BASE),
    authorization_url="{base}/oauth/authorize".format(base=HITOBITO_BASE),
    redirect_url=help.getenv('REDIRECT_URL_LOGIN'),
    scope=['email', 'name', 'with_roles', 'openid']
)

UNPROTECTED_PATH = '/oauth'


@oauth_authorized.connect
def handle_login(blueprint, token):
    # make sure the user is allowed to access the site before giving out a tokens
    response = blueprint.session.get(
        'oauth/profile', headers={'X-Scope': 'with_roles'})
    role_ids = [x['group_id'] for x in response.json()['roles']]

    if int(help.getenv('HITOBITO_GROUP')) not in role_ids:
        raise Exception(HTTPStatus.FORBIDDEN)

    if str(response.json()['id']) not in help.getenv('HITOBITO_ALLOWED_USERS').split(','):
        raise Exception(HTTPStatus.FORBIDDEN)
