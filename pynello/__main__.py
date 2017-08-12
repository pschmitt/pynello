#!/usr/bin/env python
# coding: utf-8

'''
CLI script for opening the main location's door
'''
import argparse
import logging
import sys
from pprint import pprint
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
    subparsers.add_parser('activity')
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
            pprint(activity)
    except NelloLoginException as exc:
        print(exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
