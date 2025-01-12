from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, int_pk

from enum import Enum

class Statusvalue (str, Enum):
    pending = 'ожидание'
    cancelled = 'отменена'
    completed = 'выполнена'

class Transaction(Base):
    id: Mapped[int_pk]
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    summ: Mapped[float]
    purpose: Mapped[str]
    status: Mapped[Statusvalue] = mapped_column(default=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "summ": self.summ,
            "purpose": self.purpose,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
