import binascii
from os import urandom as generate_bytes

from knightauth.settings import knight_auth_settings

hash_func = knight_auth_settings.SECURE_HASH_ALGORITHM


def create_token_string():
    return binascii.hexlify(
        generate_bytes(int(knight_auth_settings.AUTH_TOKEN_CHARACTER_LENGTH / 2))
    ).decode()


def make_hex_compatible(token: str) -> str:
    return binascii.unhexlify(binascii.hexlify(bytes(token, 'utf-8')))


def hash_token(token: str) -> str:
    digest = hash_func()
    digest.update(make_hex_compatible(token))
    return digest.hexdigest()
