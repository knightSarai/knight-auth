from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed

USER_SETTINGS = getattr(settings, 'KNIGHT_AUTH', {})
ISO_8601 = 'iso-8601'


DEFAULTS = {
    'SECURE_HASH_ALGORITHM': 'hashlib.sha512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=10),
    'USER_SERIALIZER': None,
    'TOKEN_LIMIT_PER_USER': None,
    'AUTO_REFRESH': False,
    'MIN_REFRESH_INTERVAL': 60,
    'AUTH_HEADER_PREFIX': 'Token',
    'EXPIRY_DATETIME_FORMAT': ISO_8601,
    'TOKEN_MODEL': getattr(settings, 'KNIGHT_AUTH_MODEL', 'core.AuthToken'),
    'TOKEN_PREFIX': '',
}

DEFAULTS.update(**USER_SETTINGS)


class KnightAuthSettings:
    def __init__(self, **entries):
        self.__dict__.update(entries)


knight_auth_settings = KnightAuthSettings(**DEFAULTS)


def reload_api_settings(*args, **kwargs):
    global knight_auth_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'KNIGHT_AUTH':
        knight_auth_settings = KnightAuthSettings(**value)
        if len(knight_auth_settings.TOKEN_PREFIX) > CONSTANTS.MAXIMUM_TOKEN_PREFIX_LENGTH:
            raise ValueError("Illegal TOKEN_PREFIX length")


setting_changed.connect(reload_api_settings)


class CONSTANTS:
    TOKEN_KEY_LENGTH = 15
    DIGEST_LENGTH = 128
    MAXIMUM_TOKEN_PREFIX_LENGTH = 10

    def __setattr__(self, *args, **kwargs):
        raise Exception('''
            Constant values must NEVER be changed at runtime, as they are
            integral to the structure of database tables
            ''')


CONSTANTS = CONSTANTS()
