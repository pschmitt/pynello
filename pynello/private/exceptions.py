'''
Nello Exceptions
'''


class NelloException(Exception):
    '''
    Base Exception for Nello related errors
    '''
    pass


class NelloLoginException(NelloException):
    '''
    Exception to be raised when the login fails
    '''
    pass


class NelloTokenTimeoutException(NelloException):
    '''
    Exception to be raised when the auth ticket expires
    '''
    pass
