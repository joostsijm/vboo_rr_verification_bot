"""PACC API functions"""

import re

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from app import BASE_URL, HEADERS, LOGGER

class PlayerNotFoundException(Exception):
    """RR exception"""
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        LOGGER.warning('PlayerNotFoundException')


def get_rr_player(player_id):
    """Get Rival Region player"""
    response = requests.get(
        '{}slide/profile/{}'.format(BASE_URL, player_id),
        headers=HEADERS
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    player = {
        'name': None,
        'region': None,
        'residency': None,
        'registation_date': None,
    }
    table = soup.find('table')
    if table is None:
        raise PlayerNotFoundException('Player {} not found'.format(player_id))
    name = soup.find('h1')
    if name:
        player['name'] = re.sub(r'.*:\s', '', name.text)
    for row in table.find_all('tr'):
        label = row.find('td').text.strip() 
        if label == 'Region:':
            span = row.find('span', {'class': 'dot'})
            if span:
                player['region'] = span.text
        if label == 'Residency:':
            span = row.find('span', {'class': 'dot'})
            if span:
                player['residency'] = span.text
        if label == 'Registration date:':
            element = row.find('td', {'class': 'imp'})
            if element:
                player['registation_date'] = parser.parse(element.text)

    return player

def get_players_by_name(player_name):
    """Get player list by name"""
    response = requests.get(
        '{}listed/region/0/{}/0'.format(BASE_URL, player_name),
        headers=HEADERS,
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    players = []
    player_items = soup.find_all('tr', {'class': 'list_link'})
    for player_item in player_items:
        players.append({
            'id': int(player_item.get('user')),
            'name': player_item.find('td', {'class': 'list_name'}).text.strip(),
            'level': int(player_item.find('td', {'class': 'list_level'}).text),
        })
    return players

def send_personal_message(user_id, message):
    """Send personal message to player"""
    requests.post(
        '{}send_personal_message/{}'.format(BASE_URL, user_id),
        headers=HEADERS,
        data={
            'message': message
        }
    )
