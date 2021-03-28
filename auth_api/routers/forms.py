from fastapi import APIRouter, Depends, Form
from auth_api.lib_cfg import config
from auth_api.models import (
    UserCreate
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


@router.post("/u/new", tags=["users"])
async def new_user(
        fname: str = Form(...),
        lname: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        interest: str = Form(...),
        profession: str = Form(...),
        description: str = Form(...),
        repo=Depends(get_user_repo)):

    UC = UserCreate(
        fname=fname,
        lname=lname,
        email=email,
        password=password,
        interest=interest,
        profession=profession,
        description=description,
        username=None,
        ukey=None,
        salt=None,
    )
    print(UC)
    return ""
