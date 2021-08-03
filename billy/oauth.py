import env

from http import HTTPStatus
from dotenv import load_dotenv
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized

dance = OAuth2ConsumerBlueprint(
    "billy", __name__,
    client_id=env.HITOBITO_OAUTH_CLIENT_ID,
    client_secret=env.HITOBITO_OAUTH_SECRET,
    base_url=env.HITOBITO_HOST,
    token_url="{base}/oauth/token".format(base=env.HITOBITO_HOST),
    authorization_url="{base}/oauth/authorize".format(base=env.HITOBITO_HOST),
    redirect_url=env.REDIRECT_URL_LOGIN,
    scope=['email', 'name', 'with_roles', 'openid']
)

UNPROTECTED_PATH = '/oauth'


@oauth_authorized.connect
def handle_login(blueprint, token):
    # make sure the user is allowed to access the site before giving out a tokens
    response = blueprint.session.get(
        'oauth/profile', headers={'X-Scope': 'with_roles'})
    role_ids = [x['group_id'] for x in response.json()['roles']]

    if env.HITOBITO_GROUP not in role_ids:
        raise Exception(HTTPStatus.FORBIDDEN)

    if str(response.json()['id']) not in env.HITOBITO_ALLOWED_USERS.split(','):
        raise Exception(HTTPStatus.FORBIDDEN)
