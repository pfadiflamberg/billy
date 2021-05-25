import os
import sys
import requests

from dotenv import load_dotenv
from flask import Flask
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

# TODO: check if url points to hitobito-server, otherwise throw some exception

def hitobito(request):
    assert(not request.startswith('/'))
    url = os.path.join(hitobitoServer, hitobitoLang, request) + '.json'
    response = session.get(url=url)
    response.raise_for_status()
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

def getMailingListIDs(group_id,mailing_list_id):
    """
    Given a group ID and mailing list ID, return the IDs of all the people in that mailing list.
    """
    response = hitobito('groups/{group}/mailing_lists/{list}'.format(group=group_id, list=mailing_list_id))
    return response['mailing_lists'][0]['links']['subscribers']

def getMailingListNameIDs(group_id, mailing_list_id):
    """
    Given a group ID and mailing list ID, return all the Names and IDs of people in that mailing list.
    """
    response = hitobito('groups/{group}/mailing_lists/{list}'.format(group=group_id, list=mailing_list_id))
    return [{'id': p['id'], 'name':getName(p)} for p in response['linked']['people']]


def getPerson(person_id):
    response = hitobito('people/{person}'.format(person=person_id))
    #logger.debug(response)
    p = getHitobitoPerson(response)
    person = {
        'id': p['id'],
        'salutation': getSalutation(p),
        'name': getName(p),
        'nickname': getNickname(p),
        'shortname': getShortname(p),
        'role': getRole(p),
        'addr': getAddress(p),
        'emails': getEmails(p),
    }
    return person


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
    # if there is a default email address only it will be returned
    emails = list()
    if hitobitoPerson['email']:
        emails.append(hitobitoPerson['email'])
    elif 'additional_emails' in hitobitoPerson['linked']:
        emails = list(map(lambda p: p['email'],
                          hitobitoPerson['linked']['additional_emails']))
    # remove duplicates
    return list(set(emails))


def getRole(hitobitoPerson):
    # TODO: suggest rover, pfadi, biber
    return 'unknown'
