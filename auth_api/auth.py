import logging
from datetime import datetime, timedelta
from typing import Optional

import yaml
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

import random
import string
from auth_api.models import TokenData, User

from .deps import logger
from .lib_cfg import config
from auth_api.repositories.users import get_user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=config.key('token'), auto_error=False)


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto", argon2__min_rounds=6)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, hashed_password, *, salt=''):
    return pwd_context.verify(f"{salt}{plain_password}", hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def auth_user(username: str, password: str, repo):
    try:
        res = await repo.getByMail(username)
        assert verify_password(password, res['pass'], salt=res['salt'])
        logger.info("Authentified user %s (%s)", res['username'], res['userid'])
        udict = {
            'email': res['email'],
            'valid': True,
            'username': res['username'],
            'admin': True,
        }
        return User(**udict)
    except KeyError as e:
        logger.exception(e)
        logger.info('Login error')
        return None
    except AssertionError:
        logger.info('Login check failed')
        return None
    except Exception as e:
        logger.exception(e)
        logger.info('Login unexpected error')
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.key(['auth', 'secret_key']),
        algorithm=config.key(['auth', 'algorithm'])
    )
    return encoded_jwt


async def get_current_user(
        token: Optional[str] = Depends(oauth2_scheme),
        repo=Depends(get_user_repo)):
    if not token:
        return False

    tokdata = decode_token(token)
    res = await repo.getByMail(tokdata.username)

    return User(
        email=res['email'],
        valid=True,
        username=res['username'],
        admin=True,
    )


def decode_token(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.key(['auth', 'secret_key']), algorithms=[config.key(['auth', 'algorithm'])])
        username: str = payload.get("sub")
        if username is None:
            logger.warning('No User Name')
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.warning('JWTError')
        raise credentials_exception
    return token_data
    # user = get_user(username=token_data.username)
    # if user is None:
    #     logger.warning('No User Found')
    #     raise credentials_exception
    # return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print(current_user)
    if not current_user:
        raise HTTPException(status_code=400, detail="Could not identify user")
    if not current_user.valid:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_user_opt(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        return False
    if not current_user.valid:
        return False
    return current_user


def generate_ukey():
    chars = string.digits + string.ascii_letters
    pre = ''.join(random.choice(chars) for i in range(4))
    suf = ''.join(random.choice(chars) for i in range(4))
    return f"{pre}-{suf}"


def generate_salt():
    return ''.join(random.choice(string.printable) for i in range(64))


def generate_SaltNPepper(password):
    salt = generate_salt()
    return salt, pwd_context.hash(f"{salt}{password}")
