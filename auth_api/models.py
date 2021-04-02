from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field, Json, PositiveInt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scope: Optional[str] = None


class DecodeModel(BaseModel):
    token: str
    env: str


class ByKeyModel(BaseModel):
    key: str
    env: str


class User(BaseModel):
    email: str
    valid: Optional[bool] = True
    username: str
    admin: bool = True


class UserData(BaseModel):
    id_internal: str
    userid: uuid.UUID
    fname: Optional[str] = '[ name ]'
    lname: Optional[str] = '[ surname ]'
    username: str
    email: str
    email_valid: Optional[bool] = True
    profession: Optional[str] = None
    password: str
    salt: str
    access_prod: Optional[str] = 'user'
    access_test: Optional[str] = 'user'
    access_staging: Optional[str] = 'user'
    access_dev: Optional[str] = 'user'


class UserInDB(User):
    hashed_password: str


class SubscribeModel(BaseModel):
    fname: str
    lname: str
    email: str
    password: str
    interest: str
    profession: str
    description: str

# class UserCreate(BaseModel):
#     userid: str
#     username: str
#     email: str
#     profession: str
#     description: str
#     ukey: str
#     password: str
#     salt: str


class UserCreate(BaseModel):
    userid: uuid.UUID
    fname: str
    lname: str
    email: str
    password: str
    interest: str
    profession: str
    description: str
    username: str
    ukey: str
    salt: str
