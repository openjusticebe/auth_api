import os
import logging
from contextlib import asynccontextmanager

from cryptography.fernet import Fernet
from fastapi import Header, HTTPException

from .lib_cfg import config
from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())


DB_POOL = False

templates = Jinja2Templates(directory="templates")
jinjaEnv = Environment(
    loader=FileSystemLoader('%s/../templates/' % os.path.dirname(__file__)))


def oj_decode(payload, env: str):
    key = config.key(['keys', env])
    f = Fernet(key)
    return f.decrypt(payload.encode()).decode()


async def get_token_header(x_token: str = Header(...)):
    if x_token != config.key('token'):
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


async def get_db():
    global DB_POOL  # pylint:disable=global-statement
    conn = await DB_POOL.acquire()
    try:
        yield conn
    finally:
        await DB_POOL.release(conn)


@asynccontextmanager
async def oj_db():
    global DB_POOL  # pylint:disable=global-statement
    conn = await DB_POOL.acquire()
    try:
        yield conn
    finally:
        await DB_POOL.release(conn)
