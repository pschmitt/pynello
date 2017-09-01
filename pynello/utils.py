'''
Misc utility functions
'''
import logging


LOGGER = logging.getLogger(__name__)


def extract_status_code(json_response):
    '''
    Extract the status code string from a JSON response
    '''
    return json_response.get('result', {}).get('status')


def extract_error_message(json_response):
    '''
    Extract the error message from an API call's JSON response
    '''
    return json_response.get('result', {}).get('message')


def check_success(json_response):
    '''
    Check whether an API call suceeded
    :param json_response: JSON response
    '''
    # The login call returns a status code of 'OK' when successful
    # The other methods should return '200'
    status_codes_ok = ['200', 'OK']
    status = extract_status_code(json_response)
    return status in status_codes_ok
