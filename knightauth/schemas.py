from ninja import Schema


class Login(Schema):
    username: str
    password: str
    