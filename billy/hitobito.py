import os
import sys
import requests

from dotenv import load_dotenv
from flask import Flask
from http import HTTPStatus
from loguru import logger
from os.path import join, dirname
from requests.adapters import HTTPAdapter

load_dotenv('./env/hitobito.env')

# we read them from the provided file
hitobitoEmail = os.getenv('HITOBITO_EMAIL')
hitobitoToken = os.getenv('HITOBITO_TOKEN')
hitobitoServer = os.getenv('HITOBITO_SERVER')
hitobitoLang = os.getenv('HITOBITO_LANG')

headers = {
    "Accept": "application/json",
    "X-User-Email": hitobitoEmail,
    "X-User-Token": hitobitoToken,
}

session = requests.Session()
session.mount(hitobitoServer, HTTPAdapter(max_retries=5))
session.headers.update(headers)


def hitobito(request):
    assert(not request.startswith('/'))
    url = os.path.join(hitobitoServer, hitobitoLang, request) + '.json'
    response = session.get(url=url)
    if not response.status_code == HTTPStatus.OK:
        logger.debug("request: {request}, response: {response}, data: {data}",
                     request=url, response=response, data=response.json())
        raise Exception('Failed to access resource.')
    return response.json()


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


def getPerson(person_id):
    response = hitobito('people/{person}'.format(person=person_id))
    logger.info(response)
    p = getHitobitoPerson(response)
    person = {
        'id': p['id'],
        'salutation': getSalutation(p),
        'role': getRole(p),
        'addr': getAddress(p),
        'emails': getEmails(p),
    }
    return person


def getAddress(hitobitoPerson):
    return '\n'.join([
        '{firstName} {lastName} / {nickname}'.format(
            firstName=hitobitoPerson['first_name'], lastName=hitobitoPerson['last_name'], nickname=hitobitoPerson['nickname']),
        '{street}'.format(
            street=hitobitoPerson['address']),
        '{zip} {town}'.format(
            zip=hitobitoPerson['zip_code'], town=hitobitoPerson['town'])
    ])


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
    # if there is a default email address only it will be returned
    emails = list()
    if hitobitoPerson['email']:
        emails.append(hitobitoPerson['email'])
    else:
        emails = list(map(lambda p: p['email'],
                          hitobitoPerson['linked']['additional_emails']))
    # remove duplicates
    return list(set(emails))


def getRole(hitobitoPerson):
    # TODO: suggest rover, pfadi, biber
    return 'unknown'
