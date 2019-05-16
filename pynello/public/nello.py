#!/usr/bin/env python
# coding: utf-8

from .nelloapiclient import NelloApiClient


# pylint: disable=too-few-public-methods
class NelloObject(object):
    '''
    Base class for Nello Objects.
    '''

    def __init__(self, nello, json):
        self._nello = nello
        self._json = json


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
            zip_code, city, state, country)

    def open_door(self):
        '''
        Open this lock
        '''
        return self._nello.open_door(self.location_id)

    def update(self):
        '''
        Update JSON data
        '''
        res = self._nello.list_locations()
        location_data = res.get('data')
        for loc in location_data:
            if loc.get('location_id') == self.location_id:
                self._json = loc

    def list_time_windows(self):
        ''' List time windows for this location '''
        return self._nello.list_time_windows(self.location_id)

    def create_time_window(self, name, ical):
        '''
        Create a new time window for this location
        :param ical: String representation of an ICAL calendar event
        '''
        return self._nello.create_time_window(self.location_id, name, ical)

    def delete_time_window(self, time_window_id):
        '''
        Delete a time window for this location
        :param time_window_id: ID of the time window to delete
        '''
        self._nello.delete_time_window(self.location_id, time_window_id)

    def set_webhook(self, url, actions=None):
        '''
        Update the webhook URL to be called on new events
        :param webhook_url: URL to invoke when an action occurs
        :param actions: List of actions for which the webhook url is to be
        called
        '''
        return self._nello.set_webhook(self.location_id, url, actions)

    def delete_webhook(self):
        '''
        Delete the current webhook for this location
        '''
        return self._nello.delete_webhook(self.location_id)

    def __str__(self):
        '''
        String representation of a NelloLocation object
        '''
        return '{} - {}'.format(self.address, self.location_id)


class Nello(object):
    '''
    Nello Intercom
    '''
    def __init__(self, client_id, username, password):
        self._api_client = NelloApiClient(client_id, username, password)

    @property
    def locations(self):
        '''
        List of locations the current user has access to
        '''
        res = self._api_client.list_locations()
        location_data = res.get('data')
        locs = []
        for loc in location_data:
            locs.append(NelloLocation(self._api_client, loc))
        return locs

    @property
    def main_location(self):
        '''
        Get the main location (lock)
        This equates to the first lock if there are multiple available
        '''
        all_locations = self.locations
        return self.locations[0] if all_locations else None
