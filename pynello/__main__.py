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
from .nello import (LOGGER, Nello, NelloLoginException)


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
    subparsers.add_parser('open')
    activity_parser = subparsers.add_parser('activity')
    activity_parser.add_argument(
        '-j', '--raw', action='store_true', default=False,
        help='Output RAW JSON')
    activity_parser.add_argument(
        '-r', '--reverse', action='store_true', default=False,
        help='Reverse output')
    return parser.parse_args()


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
        if args.location:
            target_location_id = args.location
        else:
            target_location_id = nello.main_location.location_id
        if args.action == 'open':
            if nello.open_door(target_location_id):
                print('Open door: SUCCESS!')
            else:
                print('Failed to open door')
                sys.exit(1)
        elif args.action == 'activity':
            activity = nello.get_activity(target_location_id)
            if args.reverse:
                activity = reversed(activity)
            if args.raw:
                pprint(activity)
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
    except NelloLoginException as exc:
        print(exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
