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
        :param method: HTTP method to use (GET or POST)
        :param path: URL path to the API object to call
        :param json: Optional JSON data
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
        List the available locations/locks
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/list-locations
        '''
        url = 'https://public-api.nello.io/v1/locations/'
        return self.__request('GET', url)

    def list_time_windows(self, location_id):
        ''' List time windows
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/list-time-windows
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/tw/'.format(location_id)
        return self.__request('GET', url)

    def create_time_window(self, location_id, name, ical):
        '''
        Create a new time window
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/create-a-new-time-window
        :param location_id: ID of the location
        :param ical: String representation of an ICAL calendar event
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/tw/'.format(
            location_id)
        data = {'name': name, 'ical': ical}
        return self.__request('POST', url, json=data)

    def delete_time_window(self, location_id, time_window_id):
        '''
        Delete a time window
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/delete-a-time-window
        :param location_id: ID of the location
        :param time_window_id: ID of the time window to delete
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/tw/{}/'.format(
            location_id, time_window_id)
        return self.__request('DELETE', url)

    def open_door(self, location_id):
        '''
        Open the door at a set location
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/open-door
        :param location_id: ID of the location
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/open/'.format(
            location_id)
        return self.__request('PUT', url)

    def set_webhook(self, location_id, webhook_url, actions=None):
        '''
        Set a webhook URL that is to be called when set actions occur
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/add-/-update-webhook
        :param location_id: ID of the location
        :param webhook_url: URL to invoke when an action occurs
        :param actions: List of actions for which the webhook url is to be
        called
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
        Delete the current webhook for a location
        Documentation:
        https://nellopublicapi.docs.apiary.io/#reference/0/locations-collection/delete-webhook
        :param location_id: ID of the location
        '''
        url = 'https://public-api.nello.io/v1/locations/{}/webhook/'.format(
            location_id)
        return self.__request('DELETE', url)
