from pydantic import BaseModel, Field, field_validator
from app.transactions.models import Statusvalue
from datetime import datetime
from typing import Optional

class STrunsactionRegister(BaseModel):
    recipient_id: int = Field(..., description="id пользователя кому переводят")
    summ: int = Field(..., description="id пользователя кому переводят")
    purpose: str = Field(..., max_length=100, description="Назначение перевода")

    @field_validator('summ')
    def check_summ(cls, value):
        if value <= 0:
            raise ValueError('Сумма должна быть больше нуля')
        return value

class STrunsaction(BaseModel):
    id: int = Field(..., description="id транзакции")
    sender_id: int = Field(..., description="id пользователя кто переводит")
    recipient_id: int = Field(..., description="id пользователя кому переводят")
    summ: int = Field(..., description="id пользователя кому переводят")
    purpose: str = Field(..., max_length=100, description="Назначение перевода")
    status: Statusvalue = Field(..., description="Статус транзакции")
    updated_at: datetime = Field(..., description="Статус транзакции")


class RBTrunsaction:
    def __init__(self, status: Optional[Statusvalue] = None,
                 begin: Optional[datetime] = datetime(1970, 1, 1, 0, 0, 0),
                 end: Optional[datetime] = datetime(2070, 1, 1, 0, 0, 0)):
        # self.id: Optional[int] = id
        self.status: Optional[Statusvalue] = status
        self.begin: Optional[datetime] = begin
        self.end: Optional[datetime] = end