from fastapi import Depends
from auth_api.models import (
    UserCreate,
    UserData
)
from ..deps import (
    get_db,
    logger,
)

FIELDS = """
        id_internal, name, username, email, email_valid, profession, fname, lname,
        userid, password, salt, userid,
        access_prod, access_test, access_staging, access_dev
"""

GET_USER_BY_MAIL = f"""
    SELECT
    {FIELDS}
    FROM
        users
    WHERE
        email = $1
    ORDER BY
        date_created DESC
"""

GET_USER_BY_KEY = f"""
    SELECT
    {FIELDS}
    FROM
        users
    WHERE
        ukey = $1
    ORDER BY
        date_created DESC
"""

GET_USER_BY_UID = f"""
    SELECT
    {FIELDS}
    FROM
        users
    WHERE
        userid = $1
    ORDER BY
        date_created DESC
"""

REGISTER_NEW_USER = """
    INSERT INTO users (userid, username, email, profession, description, ukey, password, salt, fname, lname, interest)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    RETURNING userid, username, email
"""

UPDATE_PASSWORD = """
    UPDATE users SET
        password = $1,
        salt = $2,
        date_updated = NOW()
    WHERE userid = $3
"""


async def get_user_repo(db=Depends(get_db)):
    return UserRepo(db)


class UserRepo:

    _db = None

    def __init__(self, db):
        self._db = db

    async def getByMail(self, email):
        res = await self._db.fetchrow(GET_USER_BY_MAIL, email)
        return UserData(**dict(res))

    async def getByKey(self, ukey):
        res = await self._db.fetchrow(GET_USER_BY_KEY, ukey)
        return UserData(**dict(res))

    async def getById(self, uid):
        res = await self._db.fetchrow(GET_USER_BY_UID, uid)
        return UserData(**dict(res))

    async def registerNewUser(self, *, user: UserCreate):
        logger.debug("Creating new user record for %s - %s", user.userid, user.username)
        res = await self._db.fetchrow(REGISTER_NEW_USER,
            user.userid,
            user.username,
            user.email,
            user.profession,
            user.description,
            user.ukey,
            user.password,
            user.salt,
            user.fname,
            user.lname,
            user.interest)
        logger.info("Created new user %s (%s)", user.username, user.userid)
        return res

    async def updateUserPassword(self, *, user: UserData):
        logger.debug("Updating password for user %s - %s", user.userid, user.username)
        await self._db.execute(UPDATE_PASSWORD,
            user.password,
            user.salt,
            user.userid)
        return True
