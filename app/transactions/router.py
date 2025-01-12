from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.future import select
from typing import Any
from app.config import logger
from app.config import get_db_url
from app.database import async_session_maker
from app.users.models import User
from app.users.dao import UsersDAO
from app.users.auth import get_current_user
from app.transactions.models import Transaction
from app.transactions.schemas import STrunsactionRegister, RBTrunsaction, STrunsaction
from app.transactions.dao import make_trans

DATABASE_URL = get_db_url()

router = APIRouter(prefix='/transaction', tags=['Transactions'])

@router.post("/send/")
async def send_cash(user_data: STrunsactionRegister, user: User = Depends(get_current_user)) -> dict:
    user_dict = user_data.dict()
    logger.info(f'Пользователь {user.id} инициировал отправку средств {user_dict}')
    recipient = await UsersDAO.find_one_or_none_by_id(user_dict['recipient_id'])
    if recipient:
        if recipient.id != user.id:
            check, mess = await make_trans(user, recipient, float(user_dict['summ']), user_dict['purpose'])
            if check:
                return {'message': f'{mess}'}
            else:
                return {'message': f'{mess}'}
        else:
            logger.info(f'Отказ в переводе средств, отправитель: {user.id}. Себе переводить средства нельзя')
            return {'message': 'Себе переводить средства нельзя'}
    else:
        logger.info(f'Отказ перевода средств, отправитель: {user.id}. Средства можно перевести только зарегистрированному пользователю')
        return {'message': 'Средства можно перевести только зарегистрированному пользователю'}

@router.get("/view/", response_model= Page[STrunsaction])
async def view_filter(request_body: RBTrunsaction = Depends()) -> Any:
    if request_body.status:
        query = (select(Transaction)
                 .filter(Transaction.updated_at <= request_body.end)
                 .filter(Transaction.updated_at >= request_body.begin)
                 .filter(Transaction.status == request_body.status))
    else:
        query = (select(Transaction)
                 .filter(Transaction.updated_at <= request_body.end)
                 .filter(Transaction.updated_at >= request_body.begin))
    async with async_session_maker() as session:
        async with session.begin():
            result = await session.execute(query)
    transactions = result.scalars().all()
    list_trnsns = [etr.to_dict() for etr in transactions]
    disable_installed_extensions_check()
    return paginate(list_trnsns)