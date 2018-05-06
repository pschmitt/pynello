#!/usr/bin/env python
# coding: utf-8

'''
CLI script for opening the main location's door
'''
import argparse
import logging
import sys
from datetime import datetime
from pprint import pprint
from dateutil import tz
from dateutil.parser import parse as dateparse
from .private.nello import (LOGGER, Nello, NelloLoginException)

FIELD_LOCATION_ID = ['id', 'location_id']
FIELD_SHORT_ID = ['sid', 'short', 'short_loc_id', 'short_location_id']
FIELD_ADDRESS = ['addr', 'address', 'adress', 'addresse']
FIELDS = FIELD_LOCATION_ID + FIELD_SHORT_ID + FIELD_ADDRESS


def parse_args():
    '''
    Parse CLI args
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument(
        '-l', '--location', default=None,
        help='Target location ID (default: Main location)')
    parser.add_argument('-D', '--debug', action='store_true', default=False)
    subparsers = parser.add_subparsers(dest='action', help='Available actions')
    subparsers.required = True
    activity_parser = subparsers.add_parser('activity')
    activity_parser.add_argument(
        '-j', '--raw', action='store_true', default=False,
        help='Output RAW JSON')
    activity_parser.add_argument(
        '-r', '--reverse', action='store_true', default=False,
        help='Reverse output')
    subparsers.add_parser('open')
    list_parser = subparsers.add_parser('list')
    list_parser.add_argument(
        '-f', '--field', choices=FIELDS, help='Field filter')
    subparsers.add_parser('info')
    return parser.parse_args()


def get_target_location_id(nello, args):
    '''Get the target location ID.'''
    return args.location if args.location else \
        nello.main_location.location_id


def open_door(nello, target):
    '''
    Open the door.
    :param nello: Nello object
    :param target: Target Location ID
    '''
    if nello.open_door(target):
        print('Door opened successfully')
    else:
        print('Failed to open door')
        sys.exit(1)


def display_activity(nello, target, raw=False, reverse=False):
    '''
    Display the recent activity.
    :param nello: Nello object
    :param target: Target Location ID
    :param raw: Raw output mode
    :param reverse: Whether to reverse the activity
    '''
    activity = nello.get_activity(target)
    if reverse:
        activity = reversed(activity)
    if raw:
        pprint(list(activity))
    else:
        for act in activity:
            # Retrive raw date
            date = dateparse(act.get('date'))
            # Convert to local time
            utc_date = date.replace(tzinfo=tz.tzutc())
            localized_date = utc_date.astimezone(tz.tzlocal())
            date_str = datetime.strftime(
                localized_date, '%Y-%m-%d %H:%M:%S')
            print('[{}] {}'.format(
                date_str,
                act.get('description')))


def list_locations(nello, location=None, field=None):
    '''
    List the available locations
    :param nello: Nello object
    :param location: Only location to display
    :param field: Optional field filter
    '''
    all_locations = nello.locations
    locations = None
    if location:
        for loc in all_locations:
            if loc.location_id == location or loc.short_id == location:
                locations = [loc]
        if not locations:
            print('Could not find any location with ID: {}'.format(location),
                  file=sys.stderr)
            sys.exit(2)
    else:
        locations = all_locations

    for loc in locations:
        output = ''
        if field:
            req_filter = field.lower()
            if req_filter in FIELD_LOCATION_ID:
                output = loc.location_id
            elif req_filter in FIELD_SHORT_ID:
                output = loc.short_id
            elif req_filter in FIELD_ADDRESS:
                output = loc.address
        else:
            output = '# Location\n' \
                     'Location ID: {}\n' \
                     'Short Location ID: {}\n' \
                     'Address: {}'.format(
                         loc.location_id, loc.short_id, loc.address)
        print(output)


def display_info(nello):
    '''
    Display general info about the current account etc.
    '''
    print('User ID: {}\n'
          'Username: {}\n'
          'First name: {}\n'
          'Last name: {}\n'.format(
              nello.account.user_id,
              nello.account.username,
              nello.account.first_name,
              nello.account.last_name))
    print('Roles:')
    for role in nello.account.roles:
        is_admin = role.get('role') == 'unrestricted'
        print('- {}: {}{}'.format(
            role.get('location_id'),
            'Admin' if is_admin else 'User',
            ' (Inactive)' if not role.get('is_active', False) else ''))


def main():
    '''
    Main CLI function
    '''
    args = parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    LOGGER.debug('Args: %s', args)
    try:
        nello = Nello(username=args.username, password=args.password)
        LOGGER.debug('Nello: %s', vars(nello))
        if args.action == 'open':
            target = get_target_location_id(nello, args)
            open_door(nello, target)
        elif args.action == 'activity':
            target = get_target_location_id(nello, args)
            display_activity(nello, target, args.raw, args.reverse)
        elif args.action == 'list':
            list_locations(nello, location=args.location, field=args.field)
        elif args.action == 'info':
            display_info(nello)
    except NelloLoginException as exc:
        print(exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
