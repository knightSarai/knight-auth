from typing import Union

from ninja import Schema
from datetime import datetime


class LoginIn(Schema):
    username: str
    password: str


class ErrorOut(Schema):
    message: Union[str, list]


class LoginSuccessOut(Schema):
    expiry: datetime
    token: str


class UserRegisterSchema(Schema):
    username: str
    email: str
    password: str
    password_confirm: str
