from fastapi import Depends
from auth_api.models import (
    UserCreate
)
from ..deps import (
    get_db,
    logger,
)

GET_USER_BY_MAIL = """
    SELECT
        id_internal, name, username, email, email_valid, profession,
        access_prod, access_test, access_staging, access_dev
    FROM
        users
    WHERE
        email = $1
    ORDER BY
        date_created DESC
"""

GET_USER_BY_KEY = """
    SELECT
        id_internal, name, username, email, email_valid, profession,
        access_prod, access_test, access_staging, access_dev
    FROM
        users
    WHERE
        ukey = $1
    ORDER BY
        date_created DESC
"""

REGISTER_NEW_USER = """
    INSERT INTO users (userid, username, email, profession, description, ukey, password, salt)
    VALUES ($s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING userid, username, email,
"""


async def get_user_repo(db=Depends(get_db)):
    return UserRepo(db)


class UserRepo:

    _db = None

    def __init__(self, db):
        self._db = db

    async def getByMail(self, email):
        res = await self._db.fetchrow(GET_USER_BY_MAIL, email)
        return res

    async def getByKey(self, ukey):
        res = await self._db.fetchrow(GET_USER_BY_KEY, ukey)
        return res

    async def registerNewUser(self, *, user: UserCreate):
        logger.debug("Creating new user record for %s - %s", user.userid, user.username)
        res = await self._db.fetchrow(REGISTER_NEW_USER, (
            user.userid,
            user.username,
            user.email,
            user.profession,
            user.description,
            user.ukey,
            user.password,
            user.salt
        ))
        return res

