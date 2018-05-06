#!/usr/bin/env python
# coding: utf-8

'''
Nello Intercom Library
Credit: https://forum.fhem.de/index.php/topic,75127.msg668871.html
'''

import logging
import requests
from .exceptions import (NelloLoginException, NelloTokenTimeoutException)
from .utils import (check_success, extract_error_message, extract_status_code)

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class NelloObject(object):
    '''
    Base class for Nello Objects.
    '''

    def __init__(self, nello, json):
        self._nello = nello
        self._json = json


class NelloAccount(NelloObject):
    '''
    Nello Account information
    '''

    @property
    def user_id(self):
        '''
        User ID
        '''
        return self._json.get('user_id')

    @property
    def username(self):
        '''
        Username (email)
        '''
        return self._json.get('username')

    @property
    def first_name(self):
        '''
        First Name
        '''
        return self._json.get('first_name')

    @property
    def last_name(self):
        '''
        Last Name
        '''
        return self._json.get('last_name')

    @property
    def roles(self):
        '''
        Roles (permissions)
        Example:
        [{'home_ssid': None,
          'is_active': True,
          'location_id': 'XXX',
          'role': 'unrestricted',
          'stripe_id': 'XXX',
          'subscription_plan': ''}]
        '''
        return self._json.get('roles')


class NelloLocation(NelloObject):
    '''
    Class representation of a Nello Lock.
    '''

    @property
    def location_id(self):
        '''
        Location ID
        '''
        return self._json.get('location_id')

    @property
    def short_id(self):
        '''
        Location ID
        '''
        return self._json.get('short_loc_id')

    @property
    def address(self):
        '''
        Address of this location
        '''
        addr = self._json.get('address')
        if not addr:
            return
        country = addr.get('country')
        state = addr.get('state')
        city = addr.get('city')
        zip_code = addr.get('zip')
        street = addr.get('street')
        number = addr.get('number')
        german = country.lower() in ['deutschland', 'germany']
        return '{} {} {} {}{}, {}'.format(
            street if german else number,
            number if german else street,
            zip_code, city,
            '{}, '.format(state) if state != 'state' else '',
            country)

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

    def update(self):
        '''
        Update JSON data
        '''
        location_data = self._nello.get_locations()
        for loc in location_data.get('geofences'):
            if loc.get('location_id') == self.location_id:
                self._json = loc


class Nello(object):
    '''
    Nello Intercom API client
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._session = requests.Session()
        self._account = None

    @property
    def account(self):
        '''
        Account property. Will try to login if required.
        '''
        if not self._account:
            self.login()
        return self._account

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
        LOGGER.debug('Method: %s, path: %s, json: %s', method, path, json)
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
        # We never logged in. Let's do this now.
        if not self._account:
            self.login()
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
        resp = self._request(
            method='POST',
            path='login',
            json={'username': self.username, 'password': self.password}
        )
        if not resp.get('authentication'):
            LOGGER.error('Authentication failed: %s', resp)
            err_msg = extract_error_message(resp)
            raise NelloLoginException('Login failed: {}'.format(err_msg))
        self._account = NelloAccount(self, resp.get('user'))
        LOGGER.info('Login successful. User ID: %s', self.account.user_id)
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
        path = 'locations/{}/users/{}/open'.format(
            location_id, self.account.user_id)
        resp = self._retry_request(
            method='POST',
            path=path,
            json={'type': 'swipe'}
        )
        return check_success(resp)
