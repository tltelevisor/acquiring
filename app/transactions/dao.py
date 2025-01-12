from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError
from app.config import logger
from app.database import async_session_maker
from app.dao.base import BaseDAO
from app.users.models import User
from app.transactions.models import Transaction, Statusvalue


class TransactionsDAO(BaseDAO):
    model = Transaction

async def make_trans(sender, recipient, summ, text):
    try:
        # Добавляем транзакцию в статусе "ожидание"
        trns = await TransactionsDAO.add(sender_id=sender.id, recipient_id=recipient.id, summ=summ, purpose=text, status=Statusvalue.pending)
        # Если успешно добавилась - дальнейшая обработка
        if trns:
            # Если баланс отправителя больше перечисляемой ссуммы - отправляем
            if sender.balance >= summ:
            # В одну транзакцию
                async with async_session_maker() as session:
                    async with session.begin():
                        query = (
                            sqlalchemy_update(Transaction)
                            .where(Transaction.id == trns.id)
                            .values(status=Statusvalue.completed)
                            .execution_options(synchronize_session="fetch")
                        )
                        await session.execute(query)
                        query = (
                            sqlalchemy_update(User)
                            .where(User.id == sender.id)
                            .values(balance=sender.balance - summ)
                            .execution_options(synchronize_session="fetch")
                        )
                        await session.execute(query)
                        query = (
                            sqlalchemy_update(User)
                            .where(User.id == recipient.id)
                            .values(balance=sender.balance + summ)
                            .execution_options(synchronize_session="fetch")
                        )
                        await session.execute(query)
                        try:
                            await session.commit()
                        except SQLAlchemyError as e:
                            await session.rollback()
                            logger.error(f"rollback не удался. trns.id: {trns.id}, отправитель: {sender}, Error: {e}")
                            return False, "Ошибка отмены транзакции. Обратитесь в техподдержку"
                        return True, "Средства переведены"
            else:
                await TransactionsDAO.update(filter_by={'id': trns.id}, status=Statusvalue.cancelled)
                logger.info(f'Отказ в переводе средств, отправитель: {sender}. Недостаточно средств')
                return False, 'Недостаточно средств'
        else:
            logger.error(f'Ошибка добавления транзакции, отправитель: {sender}')
            return False, 'Ошибка добавления транзакции'
    except Exception as err:
        logger.error(f"Ошибка обработки транзакции, отправитель: {sender}, Error {err}")
        return False, "Ошибка обработки транзакции"
