from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string


USER_SETTINGS = getattr(settings, 'KNIGHT_AUTH', {})

IMPORT_STRINGS = [
    'SECURE_HASH_ALGORITHM',
    'USER_SERIALIZER',
]

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
    'TOKEN_MODEL': getattr(settings, 'KNIGHT_AUTH_MODEL', 'knightauth.AuthToken'),
    'TOKEN_PREFIX': '',
}


def perform_import(val, setting_name):
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class APISettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'KNIGHT_AUTH', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if attr in self.import_strings:
            val = perform_import(val, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


knight_auth_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    global knight_auth_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'KNIGHT_AUTH':
        knight_auth_settings = APISettings(**value)
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
