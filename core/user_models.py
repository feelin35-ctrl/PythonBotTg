from pydantic import BaseModel
from typing import Optional

class UserRegistrationData(BaseModel):
    username: str
    email: str
    password: str

class UserLoginData(BaseModel):
    username: str
    password: str

class UserTokenData(BaseModel):
    bot_id: str
    token: str

class AuthData(BaseModel):
    password: str