import os
import requests

from dotenv import load_dotenv
from flask import Flask
from loguru import logger
from os.path import join, dirname
from requests.adapters import HTTPAdapter

load_dotenv('./env/hitobito.env')
hitobitoEmail = os.getenv('HITOBITO_EMAIL')
hitobitoToken = os.getenv('HITOBITO_TOKEN')
hitobitoServer = os.getenv('HITOBITO_SERVER')

headers = {
    "Accept": "application/json",
    "X-User-Email": hitobitoEmail,
    "X-User-Token": hitobitoToken,
}

session = requests.Session()
session.mount(hitobitoServer, HTTPAdapter(max_retries=5))
session.headers.update(headers)


def hitobito():
    return session


def url(base):
    assert(not base.startswith('/'))
    return os.path.join(hitobitoServer, base) + '.json'


logger.info(headers)

pathPerson = 'people/{person}'

logger.info(pathPerson.format(person=43867))
logger.info(url(pathPerson.format(person=43867)))
logger.info(hitobito().get(url=url(pathPerson.format(person=43867))))
