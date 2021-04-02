from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from auth_api.lib_cfg import config
from auth_api.models import (
    Token,
)
from auth_api.auth import (
    auth_user,
    create_access_token,
    SCOPE_DEV,
    SCOPE_STAGING,
    SCOPE_TESTING,
    SCOPE_PROD,
)
from auth_api.repositories.users import get_user_repo

router = APIRouter()


@router.post("/token", response_model=Token, tags=["authentication"])
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        repo=Depends(get_user_repo)):
    """
    Submit username/password form to this endpoint to obtain auth token

    The obtained token must be used as bearer auth in the authentication headers.
    """
    # FIXME: Some other auth provider then airtable would be nice
    # FIXME: Add support for scopes (like admin, moderatore, ...)
    # FIXME: Add password hashing support
    user = await auth_user(form_data.username, form_data.password, repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scopes = dict(x.split(':') for x in form_data.scopes)
    payload = {
        "sub": user.email,
        'env': get_scope(scopes.get('host', ''))
    }
    print(payload)
    access_token_expires = timedelta(minutes=config.key(['auth', 'expiration_minutes']))
    access_token = create_access_token(
        data=payload, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_scope(scope):
    tests = [
        ('127.0.0.1', SCOPE_DEV),
        ('localhost', SCOPE_DEV),
        ('outil.test.openjustice.be', SCOPE_STAGING),
        ('outil.openjustice.be', SCOPE_PROD),
    ]
    for url, env in tests:
        if scope.startswith(url):
            return env

    return SCOPE_DEV
