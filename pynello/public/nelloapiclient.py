#!/usr/bin/env python
# coding: utf-8

'''
Nello Intercom Library
https://nellopublicapi.docs.apiary.io
https://nelloauth.docs.apiary.io
'''

import logging

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


LOGGER = logging.getLogger(__name__)


class NelloApiClient(object):
    '''
    Nello API client
    '''
    def __init__(self, client_id, username, password):
        self._username = username
        self._password = password
        self._client_id = client_id
        client = LegacyApplicationClient(client_id=client_id)
        self._session = OAuth2Session(client=client)
        self._token = self._fetch_token()

    def _fetch_token(self):
        '''
        https://nelloauth.docs.apiary.io/#reference/0/token/create-a-new-token-password
        '''
        token_url = 'https://auth.nello.io/oauth/token/'
        return self._session.fetch_token(
            token_url=token_url,
            username=self._username,
            password=self._password,
            client_id=self._client_id
        )

    def __request(self, method, url, json=None):
        '''
        Requests wrapper
        '''
        res = self._session.request(method, url, json=json)
        res.raise_for_status()
        res_j = res.json()
        LOGGER.debug("JSON Response: %s", res_j)
        if not res_j.get('result', {}).get('success'):
            LOGGER.warning("API call was unsuccesful: %s", res_j)
        return res_j

    def list_locations(self):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/list-locations
        '''
        url = 'https://public-api.nello.io/v1/locations/'
        return self.__request('GET', url)

    def create_time_window(self, location_id, name, ical):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/create-a-new-time-window
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/tw/'.format(
            location_id)
        data = {'name': name, 'ical': ical}
        return self.__request('POST', url, json=data)

    def delete_time_window(self, location_id, time_window_id):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/delete-a-time-window
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/tw/{}/'.format(
            location_id, time_window_id)
        return self.__request('DELETE', url)

    def open_door(self, location_id):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/open-door
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/open/'.format(
            location_id)
        return self.__request('PUT', url)

    def set_webook(self, location_id, webhook_url, actions=None):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/add-/-update-webhook
        '''
        all_actions = ['swipe', 'geo', 'tw', 'deny']
        url = 'https://public-api.nello.io/v1/locations/{}/webhook/'.format(
            location_id)
        if not actions:
            # Default to all actions
            actions = all_actions
        else:
            if not isinstance(actions, list):
                raise RuntimeError("Actions: Expected a list but got "
                                   "{}".format(type(actions)))
            # Check provided action validity
            for act in actions:
                if act not in all_actions:
                    raise RuntimeError("Invalid action: {}".format(act))
        data = {'url': webhook_url, 'actions': actions}
        return self.__request('PUT', url, json=data)

    def delete_webhook(self, location_id):
        '''
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/delete-webhook
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/webhook/'.format(
            location_id)
        return self.__request('DELETE', url)
