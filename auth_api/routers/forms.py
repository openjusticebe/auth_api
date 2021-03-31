from fastapi import APIRouter, Depends, Form
from auth_api.lib_cfg import config
from auth_api.models import (
    UserCreate
)
import uuid
from ..auth import (
    get_current_active_user,
    decode_token,
    credentials_exception,
    get_current_active_user_opt,
    generate_ukey,
    generate_SaltNPepper,
    decode_reset_password_token,
    reset_password_token
)
from ..deps import (
    get_db,
    logger,
    oj_decode,
)
from datetime import timedelta
from ..lib_mail import notify

from auth_api.repositories.users import get_user_repo

router = APIRouter()


@router.post("/f/new_user", tags=["users"])
async def new_user(
        fname: str = Form(...),
        lname: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        interest: str = Form(...),
        profession: str = Form(...),
        description: str = Form(...),
        repo=Depends(get_user_repo)):

    # TODO :  Create internal fields
    # - generate username
    # - generate ukey
    # - generate salt
    # - generate password hash (or let that to the repo)
    salt, phash = generate_SaltNPepper(password)

    UC = UserCreate(
        userid=uuid.uuid4(),
        fname=fname,
        lname=lname,
        email=email,
        password=phash,
        interest=interest,
        profession=profession,
        description=description,
        username=f"{fname[0]}. {lname}",
        ukey=generate_ukey(),
        salt=salt,
    )

    res = await repo.registerNewUser(user=UC)

    await notify(email, 'new_account', {'fname': fname, 'lname': lname})

    return {
        'username': res['username'],
        'userid': res['userid']
    }


@router.post("/f/lost_password", tags=["users"])
async def lost_password(
        email: str = Form(...),
        repo=Depends(get_user_repo)):
    user = await repo.getByMail(email)
    token = reset_password_token(user, timedelta(hours=2))
    await notify(email, 'lost_password', {
        'fname': user.fname,
        'lname': user.lname,
        'token': token
    })
    return {'result': True}


@router.post("/f/reset_password", tags=["users"])
async def lost_password(
        token: str = Form(...),
        password: str = Form(...),
        repo=Depends(get_user_repo)):
    userid = decode_reset_password_token(token)
    salt, phash = generate_SaltNPepper(password)
    user = await repo.getById(userid)
    user.password = phash
    user.salt = salt
    await repo.updateUserPassword(user=user)

    return {
        'username': user.email,
        'userid': user.userid
    }
