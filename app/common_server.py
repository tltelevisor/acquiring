from fastapi import FastAPI
from app.users.router import router as router_users
from app.transactions.router import router as router_transactions
from fastapi_pagination import add_pagination

app = FastAPI()
add_pagination(app)

@app.get("/")
def home_page():
    return {"message": "Авторизуйтесь..."}

app.include_router(router_users)
app.include_router(router_transactions)