LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file_django': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose'
        },
        'file_api_v1': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/api_v1.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_django'],
            'level': 'INFO',
            'propagate': True,
        },
        'api_v1': {
            'handlers': ['file_api_v1', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
