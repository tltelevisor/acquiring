from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.config import logger
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth, SUserChngPssw
from app.users.dao import UsersDAO
from app.users.auth import (get_password_hash, get_current_user,
                            create_access_token, authenticate_user, verify_password)

router = APIRouter(prefix='/users', tags=['Users'])

@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_all(email=user_data.email)
    if user:
        logger.info(f'Пользователь {user_data.email}, {user_data.first_name}, {user_data.last_name} пытался повторно зарегистироваться')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    logger.info(f'Пользователь {user_data.email} зарегистировался')
    return {'message': 'Вы успешно зарегистрированы!'}

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    logger.info(f'Пользователь {user_data.email} аутентифицирован')
    return {'access_token': access_token}

@router.get("/account/")
async def get_account(user_data: User = Depends(get_current_user)):
    logger.info(f'Пользователь {user_data.email} авторизован, информация выдана')
    return user_data

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Вы вышли из системы'}

@router.put("/chpsswd")
async def change_passwd(user_data: SUserChngPssw, user: User = Depends(get_current_user)):
    if user:
        user_dict = user_data.dict()
        if verify_password(plain_password=user_dict['password'], hashed_password=user.password):
            logger.info(f'Пользователь {user.email} запросил смену пароля')
            check = await UsersDAO.update(filter_by={'id': user.id},
                                           password=get_password_hash(user_dict['new_password']))
            if check:
                logger.info(f'Пользователю {user.email} пароль изменен')
                return {'message': 'Пароль изменен'}
            else:
                logger.info(f'Ошибка при изменении пароля по запросу пользователя {user.email}')
                return {'message': 'Ошибка при изменении пароля'}
        else:
            logger.info(f'Пользователем {user.email} введен неверный старый пароль при его смене')
            return {'message': 'Неверный старый пароль'}
    else:
        logger.info(f'Попытка смены пароля без авторизации')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Авторизуйтесь!')

