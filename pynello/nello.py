#!/usr/bin/env python
# coding: utf-8

'''
Nello Intercom Library
Credit: https://forum.fhem.de/index.php/topic,75127.msg668871.html
'''

import logging
import requests
from .exceptions import (NelloLoginException, NelloTokenTimeoutException)
from .utils import (
    check_success, extract_error_message, extract_status_code, hash_password)

LOGGER = logging.getLogger(__name__)


class NelloLocation(object):
    '''
    Class representation of a Nello Lock
    '''
    def __init__(self, nello, json):
        self._nello = nello
        self._json = json

    @property
    def location_id(self):
        '''
        Location ID
        '''
        return self._json.get('location_id')

    @property
    def address(self):
        '''
        Address of this location
        '''
        return self._json.get('address')

    @property
    def activity(self):
        '''
        Recent activity on this lock
        '''
        return self._nello.get_activity(self.location_id)

    def open_door(self):
        '''
        Open this lock
        '''
        return self._nello.open_door(self.location_id)


class Nello(object):
    '''
    Nello Intercom API client
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._session = requests.Session()
        self.user_id = None
        self.login()

    @property
    def locations(self):
        '''
        List of locations the current user has access to
        '''
        location_data = self.get_locations()
        locs = []
        for loc in location_data.get('geofences'):
            locs.append(NelloLocation(self, loc))
        return locs

    @property
    def main_location(self):
        '''
        Get the main location (lock)
        This equates to the first lock if there are multiple available
        '''
        all_locations = self.locations
        return self.locations[0] if all_locations else None

    def _request(self, method, path, json=None):
        '''
        Issue an API call.
        NOTE: This method does not try to log in again in case the
        authentication has expired. Use _retry_request() for this.
        :param method: HTTP method to use (GET or POST)
        :param path: URL path to the API object to call
        :param json: Optional JSON data
        '''
        LOGGER.info('Method: %s, path: %s, json: %s', method, path, json)
        url = 'https://api.nello.io/{}'.format(path)
        LOGGER.debug('%s call to %s', method, url)
        LOGGER.debug('JSON Data: %s', json)
        response = self._session.request(method=method, url=url, json=json)
        response.raise_for_status()
        json_response = response.json()
        LOGGER.debug('JSON response: %s', json_response)
        if not check_success(json_response):
            status = extract_status_code(json_response)
            err_msg = extract_error_message(json_response)
            LOGGER.warning('JSON status: %s', status)
            LOGGER.warning('API Error message: %s', err_msg)
            if status == '400':
                raise NelloTokenTimeoutException(err_msg)
        return json_response

    def _retry_request(self, *args, **kwargs):
        '''
        Issue an API call that may required to log in again.
        :param method: HTTP method to use (GET or POST)
        :param path: URL path to the API object to call
        :param json: Optional JSON data
        '''
        try:
            json_response = self._request(*args, **kwargs)
        except NelloTokenTimeoutException:
            if self.login():
                json_response = self._request(*args, **kwargs)
        return json_response

    def login(self):
        '''
        Login to Nello server
        '''
        pwd_hash = hash_password(self.username, self.password)
        resp = self._request(
            method='POST',
            path='login',
            json={'username': self.username, 'password': pwd_hash}
        )
        if not resp.get('authentication'):
            LOGGER.error('Authentication failed: %s', resp)
            err_msg = extract_error_message(resp)
            raise NelloLoginException('Login failed: {}'.format(err_msg))
        self.user_id = resp.get('user', {}).get('user_id')
        LOGGER.info('Login successful. User ID: %s', self.user_id)
        return True

    def get_locations(self):
        '''
        Get all available locations
        '''
        return self._retry_request(method='GET', path='locations/')

    def get_activity(self, location_id=None):
        '''
        Get the activity log for a location
        '''
        if not location_id:
            location_id = self.main_location.location_id
        path = 'locations/{}/activity'.format(location_id)
        resp = self._retry_request(method='GET', path=path)
        return resp.get('activities')

    def open_door(self, location_id=None):
        '''
        Ring the buzzer AKA open the door
        :param location: Target location ID
        '''
        if not location_id:
            location_id = self.main_location.location_id
        path = 'locations/{}/users/{}/open'.format(location_id, self.user_id)
        resp = self._retry_request(
            method='POST',
            path=path,
            json={'type': 'swipe'}
        )
        return check_success(resp)
