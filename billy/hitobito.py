import os
import re
import requests
import error
import env
from oauth import dance
from requests.adapters import HTTPAdapter
from loguru import logger
# Use this - once db.scout.ch provides the API scope
#################################################################

# session = oauth.dance.session

# def hitobito(request):
#     assert(not request.startswith('/'))
#     path = os.path.join(HITOBITO_LANG, request) + '.json'
#     response = session.get(url=path)
#     response.raise_for_status()
#     return response.json()
#################################################################
# instead of this:
#################################################################

headers = {
    "Accept": "application/json",
    "X-User-Email": env.HITOBITO_TOKEN_USER,
    "X-User-Token": env.HITOBITO_TOKEN,
}

session = requests.Session()
session.mount(env.HITOBITO_HOST, HTTPAdapter(max_retries=5))
session.headers.update(headers)


def hitobito(request):
    url = os.path.join(env.HITOBITO_HOST,
                       env.HITOBITO_LANG, request) + '.json'
    response = session.get(url=url)
    response.raise_for_status()
    return response.json()

#################################################################


def getGroups(group_id):
    """
    Given a group ID return the group ID of that group and all decending groups.
    """
    def getGroupsRek(group_id, checked):
        groups = list()
        response = hitobito('groups/{group}'.format(group=group_id))
        checked.append(group_id)
        try:
            groups += response['groups'][0]['links']['children']
        except:
            pass
        for g in groups:
            if g not in checked:
                groups += getGroupsRek(g, checked)
        return groups
    return getGroupsRek(group_id, list())


def getGroupPeopleIDs(group_id):
    """
    Given a group ID return the IDs of all the people in that group.
    """
    response = hitobito('groups/{group}/people'.format(group=group_id))
    return list(map(lambda x: x['id'], response['people']))


def getMailingListRecipients(mailing_list_url):
    """
    Given a mailing_list url, return all the recipients (IDs, Names).
    """
    p = re.compile('(groups\/[0-9]+\/mailing_lists\/[0-9]+)')
    try:
        path = p.search(mailing_list_url).group(0)
    except:
        raise error.InvalidMailingListURL(mailing_list_url)
    response = hitobito(path)
    return {int(p['id']): p for p in response['linked']['people']}


def parseMailingListPerson(person, verify=True):

    if verify:
        if len(getEmails(person)) < 1:
            raise error.RecipientRequiresEmail(person['id'])
        for attr in ['address', 'zip_code', 'town']:
            if person[attr] and len(person[attr]) < 1:
                raise error.RecipientAddressError(person['id'])
    return {
        'id': person['id'],
        'name': getName(person),
        'salutation': "Hallo " + person.get('nickname', person['first_name']),
        'nickname': getNickname(person),
        'shortname': getShortname(person),
        'role': getRole(person),
        'addr': getAddress(person),
        'emails': getEmails(person),
    }


def parseHitobitoPerson(person):
    return {
        'id': person['id'],
        'salutation': getSalutation(person),
        'name': getName(person),
        'nickname': getNickname(person),
        'shortname': getShortname(person),
        'role': getRole(person),
        'addr': getAddress(person),
        'emails': getEmails(person),
    }

def getRawPerson(person_id):
    response = hitobito('people/{person}'.format(person=person_id))
    p = getHitobitoPerson(response)
    p['list_emails'] = getEmails(p)
    return p

def getPerson(person_id):
    response = hitobito('people/{person}'.format(person=person_id))
    p = getHitobitoPerson(response)
    return parseHitobitoPerson(p)


def getUser():
    session = dance.session
    response = session.get('oauth/profile', headers={'X-Scope': 'with_roles'})
    return parseHitobitoPerson(response.json())


def getShortname(hitobitoPerson):
    nickname = getNickname(hitobitoPerson)
    if nickname:
        return nickname
    return hitobitoPerson['first_name']


def getName(hitobitoPerson):
    return '{firstName} {lastName}'.format(
        firstName=hitobitoPerson['first_name'],
        lastName=hitobitoPerson['last_name'])


def getNickname(hitobitoPerson):
    nickname = hitobitoPerson['nickname']
    if 0 == len(nickname):
        return None
    return '{nickname}'.format(
        nickname=hitobitoPerson['nickname'])


def getAddress(hitobitoPerson):
    return {
        'street': hitobitoPerson['address'],
        'zip': hitobitoPerson['zip_code'],
        'town': hitobitoPerson['town'],
    }


def getHitobitoPerson(raw):
    p = raw['people'][0]
    p['linked'] = raw['linked']
    return p


def getSalutation(hitobitoPerson):
    # we use this instead of 'salutation_value' because hitobito does not check if the nickname is set or not
    if hitobitoPerson['gender'] == 'm':
        salutation = "Lieber"
    elif hitobitoPerson['gender'] == 'w':
        salutation = "Liebe"
    else:
        salutation = "Hallo"
    salutation += " "
    if not hitobitoPerson['nickname'] == '':
        salutation += hitobitoPerson['nickname']
    else:
        salutation += hitobitoPerson['first_name']
    return salutation


def getEmails(hitobitoPerson):
    emails = []
    if 'linked' in hitobitoPerson and 'additional_emails' in hitobitoPerson['linked']:
        emails = [entry['email'] for entry in hitobitoPerson['linked']['additional_emails']]
    if hitobitoPerson['email']:
        emails.append(hitobitoPerson['email'])
    if 'list_emails' in hitobitoPerson:
        emails += hitobitoPerson['list_emails']
    # sort and remove duplicates
    emails = list(set(emails))
    emails.sort()
    return emails


def getRole(hitobitoPerson):
    # TODO: suggest rover, pfadi, biber
    return 'unknown'
