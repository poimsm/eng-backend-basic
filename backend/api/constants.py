class AppMsg:
    UNKNOWN_ERROR = {
        'error_code': 'ERR0000',
        'message': 'Unknown error'
    }
    ID_NOT_FOUND = {
        'error_code': 'ERR0001',
        'message': 'ID does not match any resource'
    }
    INVALID_DATA = {
        'error_code': 'ERR0002',
        'message': 'Invalid data format'
    }
    OFENSIVE_STATEMENT = {
        'error_code': 'ERR0003',
        'message': 'Offensive statement'
    }
    MISSING_FIELDS = {
        'error_code': 'ERR0004',
        'message': 'There are missing fields'
    }
    EMAIL_EXISTS = {
        'error_code': 'ERR0005',
        'message': 'Email already exists'
    }
    EMAIL_OR_PASS_INCORRECT = {
        'error_code': 'ERR0006',
        'message': 'Email or password incorrect'
    }
    TOO_MANY_ITEMS = {
        'error_code': 'ERR0006',
        'message': 'Request contains too many items'
    }
