'''
Misc utility functions
'''
import binascii
import hashlib
import logging


LOGGER = logging.getLogger(__name__)


def hash_password(username, password):
    '''
    Hash the password
    '''
    LOGGER.debug('username: %s - type: %s', username, type(username))
    LOGGER.debug('password: %s - type: %s', password, type(password))
    __salt_str = str(username) + str(password)
    salt = hashlib.sha256(__salt_str.encode()).digest()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha1', password.encode(), salt, iterations=4000, dklen=32)
    # Use this to use the str value instead of bytes
    # salt = hashlib.sha256(__salt_str.encode()).hexdigest()
    # Uncomment this when using str value of the sha256 of salt
    # pwd_hash = hashlib.pbkdf2_hmac(
    #     'sha1', password.encode(), salt.encode(), iterations=4000, dklen=32)
    pwd_hash_str = binascii.hexlify(pwd_hash).upper()
    LOGGER.debug('Hash: %s - Salt: %s', pwd_hash_str, salt)
    return pwd_hash_str.decode('utf-8')


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
