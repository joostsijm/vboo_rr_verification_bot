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

    return account

def get_accounts_by_name(account_name):
    """Get account list by name"""
    response = requests.get(
        '{}listed/region/0/{}/0'.format(BASE_URL, account_name),
        headers=HEADERS,
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    accounts = []
    account_items = soup.find_all('tr', {'class': 'list_link'})
    for account_item in account_items:
        accounts.append({
            'id': int(account_item.get('user')),
            'name': account_item.find('td', {'class': 'list_name'}).text.strip(),
            'level': int(account_item.find('td', {'class': 'list_level'}).text),
        })
    return accounts

def send_personal_message(user_id, message):
    """Send personal message to player"""
    requests.post(
        '{}send_personal_message/{}'.format(BASE_URL, user_id),
        headers=HEADERS,
        data={
            'message': message
        }
    )
