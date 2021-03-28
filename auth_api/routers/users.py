from fastapi import APIRouter, Depends
from auth_api.lib_cfg import config
from auth_api.models import (
    User,
    DecodeModel,
    ByKeyModel,
    SubscribeModel,
)
from ..auth import (
    get_current_active_user,
    decode_token,
    get_user_by_key,
    credentials_exception,
    get_current_active_user_opt,
)
from ..deps import (
    get_db,
    logger,
    oj_decode,
)
from auth_api.repositories.users import get_user_repo

router = APIRouter()


# @router.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user

# @router.get("/auth/", tags=["authentication"])
# async def auth():
#     return []


@router.post("/u/by/token", response_model=User, tags=["authentication"])
async def decode(
        query: DecodeModel,
        repo=Depends(get_user_repo)):
    tokdata = decode_token(oj_decode(query.token, query.env))
    res = await repo.getByMail(tokdata.username)

    return User(
        email=res['email'],
        valid=True,
        username=res['username'],
        admin=True,
    )


@router.post("/u/by/key", response_model=User, tags=["authentication"])
async def read_user_by_key(
        query: ByKeyModel,
        repo=Depends(get_user_repo)):
    res = await repo.getByKey(oj_decode(query.key, query.env))
    return User(
        email=res['email'],
        valid=True,
        username=res['username'],
        admin=True,
    )


@router.get("/u/", tags=["users"])
async def read_users(
        db=Depends(get_db),
        current_user: User = Depends(get_current_active_user_opt)):
    """
    List all users
    """
    if not current_user.admin:
        raise credentials_exception

    sql = """
    SELECT
        id_internal, name, username, email, email_valid, profession, access_prod, access_test, access_staging, access_dev
    FROM
        users
    ORDER BY
        date_created DESC
    """

    res = await db.fetch(sql)
    return [dict(r) for r in res]


@router.get("/u/me", response_model=User, tags=["users"])
async def read_user_me(
        repo=Depends(get_user_repo),
        current_user: User = Depends(get_current_active_user)):
    """
    Read data from connected user
    """
    res = await repo.getByMail(current_user.email)

    return User(
        email=res['email'],
        valid=res['email_valid'],
        username=res['username'],
        admin=True,
    )


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }

