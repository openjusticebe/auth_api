from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, Json, PositiveInt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


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


class UserInDB(User):
    hashed_password: str
