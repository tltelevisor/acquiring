from pydantic import BaseModel, EmailStr, Field, field_validator

class SUserRegister(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    balance: float = Field(default=100, description="Начальный баланс, по умолчанию 100 (входной бонус)")

    @field_validator('balance')
    def check_balance(cls, value):
        if value <= 0:
            raise ValueError('Баланс должен быть больше нуля')
        return value


class SUserAuth(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")

class SUserChngPssw(BaseModel):
    password: str = Field(..., min_length=5, max_length=50, description="Действующий пароль, от 5 до 50 знаков")
    new_password: str = Field(..., min_length=5, max_length=50, description="Новый пароль, от 5 до 50 знаков")