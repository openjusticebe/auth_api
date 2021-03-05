from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from auth_api.lib_cfg import config
from auth_api.models import (
    Token,
    User,
    DecodeModel,
    ByKeyModel,
)
from auth_api.auth import (
    auth_user,
    create_access_token,
    get_current_active_user,
    decode_token,
    get_user_by_key,
)
from ..deps import (
    get_db,
    oj_decode,
)

router = APIRouter()


@router.post("/token", response_model=Token, tags=["authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Submit username/password form to this endpoint to obtain auth token

    The obtained token must be used as bearer auth in the authentication headers.
    """
    # FIXME: Some other auth provider then airtable would be nice
    # FIXME: Add support for scopes (like admin, moderatore, ...)
    # FIXME: Add password hashing support
    user = auth_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.key(['auth', 'expiration_minutes']))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
async def read_users():
    return []


@router.get("/u/me", response_model=User, tags=["users"])
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    Read data from connected user
    """
    return current_user


@router.get("/u/{username}", tags=["users"])
async def read_user(username: str):
    return {
        "username": username
    }


