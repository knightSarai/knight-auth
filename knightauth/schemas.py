from ninja import Schema
from datetime import datetime


class LoginIn(Schema):
    username: str
    password: str


class LoginErrorOut(Schema):
    message: str


class LoginSuccessOut(Schema):
    expiry: datetime
    token: str
