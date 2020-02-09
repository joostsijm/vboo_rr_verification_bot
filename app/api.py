"""PACC API functions"""

import re

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from app import BASE_URL, HEADERS


def get_rr_account(account_id):
    """Get Rival Region account"""
    response = requests.get(
        '{}slide/profile/{}'.format(BASE_URL, account_id),
        headers=HEADERS
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    account = {
        'name': None,
        'region': None,
        'residency': None,
        'registation_date': None,
    }
    table = soup.find('table')
    name = soup.find('h1')
    if name:
        account['name'] = re.sub(r'.*:\s', '', name.text)
        print(account['name'])
    for row in table.find_all('tr'):
        label = row.find('td').text.strip() 
        if label == 'Region:':
            span = row.find('span', {'class': 'dot'})
            if span:
                account['region'] = span.text
        if label == 'Residency:':
            span = row.find('span', {'class': 'dot'})
            if span:
                account['residency'] = span.text
        if label == 'Registration date:':
            element = row.find('td', {'class': 'imp'})
            if element:
                account['registation_date'] = parser.parse(element.text)
    # print(region)

    return account
