from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.database import Base, str_uniq, int_pk

class User(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    balance: Mapped[float] = mapped_column(default=100)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_positive'),
    )

    @validates('balance')
    def validate_price(self, key, value):
        if value < 0:
            raise ValueError("Баланс должен быть больше нуля")
        return value