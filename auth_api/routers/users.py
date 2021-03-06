from fastapi import APIRouter, Depends
from auth_api.lib_cfg import config
from auth_api.models import (
    User,
    DecodeModel,
    ByKeyModel,
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
    oj_decode,
)

router = APIRouter()


# @router.get("/users/me/", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user

# @router.get("/auth/", tags=["authentication"])
# async def auth():
#     return []


@router.post("/u/by/token", response_model=User, tags=["authentication"])
async def decode(query: DecodeModel, db=Depends(get_db)):
    return decode_token(oj_decode(query.token, query.env))


@router.post("/u/by/key", response_model=User, tags=["authentication"])
async def read_user_by_key(query: ByKeyModel, db=Depends(get_db)):
    return get_user_by_key(oj_decode(query.key, query.env))


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
        id_internal, name, email, email_valid, profession, access_prod, access_test, access_staging, access_dev
    FROM
        users
    ORDER BY
        date_created DESC
    """

    res = await db.fetch(sql)
    return [dict(r) for r in res]


@router.get("/u/me", response_model=User, tags=["users"])
async def read_user_me(
        db=Depends(get_db),
        current_user: User = Depends(get_current_active_user)):
    """
    Read data from connected user
    """
    # FIXME: Use userid instead of something else
    sql = """
    SELECT
        id_internal, name, email, email_valid, profession, access_prod, access_test, access_staging, access_dev
    FROM
        users
    WHERE
        email = $1
    ORDER BY
        date_created DESC
    """
    res = await db.fetch(sql, current_user.email)
    return [dict(r) for r in res]


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }


