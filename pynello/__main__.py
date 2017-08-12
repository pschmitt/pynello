#!/usr/bin/env python
# coding: utf-8

'''
CLI script for opening the main location's door
'''
import argparse
import logging
import sys
from .nello import (LOGGER, Nello, NelloLoginException)


def parse_args():
    '''
    Parse CLI args
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-D', '--debug', action='store_true', default=False)
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
        if nello.main_location.open_door():
            print('Open door: SUCCESS!')
        else:
            print('Failed to open door')
            sys.exit(1)
    except NelloLoginException as exc:
        print(exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
