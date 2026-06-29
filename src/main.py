from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from random import randrange

app = FastAPI()

client_accounts = []
Buy_stocks = []

class account(BaseModel):
    name: str
    number: Optional[int] = None
    amount: Optional[int] = 0

class stocks(BaseModel):
    id: Optional[int] = None
    S_name: str
    Qty: int

S_name = ["VOO", "SPYDR", "AWS", "APPL", "TSMC"]

@app.get("/")
async def root():
    return {"Welcome to Portfolio"}

@app.get("/accounts")
def get_accounts():
    return {"Account Details": client_accounts}

@app.post("/accounts", status_code = status.HTTP_201_CREATED)
def create_account(acc_list: List[account]):
    new_acc = []
    for acc in acc_list:
        acc_dict = acc.dict()
        system_generated_number = randrange(0,100_000)
        acc_dict["number"] = system_generated_number
        client_accounts.append(acc_dict)
        new_acc.append(acc_dict)
    return {"Status": "Success", "Account Detail": new_acc}

@app.post("/accounts/stocks")
def buy_stock(s_list: List[stocks]):
    listed_stocks = []
    non_listed_stocks = []
    for s in s_list:
        s_dict = s_dict()
        if s_dict["S_name"] in S_name:
            system_generated_number = randrange(0,100_000)
            s_dict["id"] = system_generated_number
            Buy_stocks.append(s_dict)
            listed_stocks.append(s_dict)
        else:
            non_listed_stocks.append(s_dict)
    return {"Approve Stocks": listed_stocks,
            "Non Approved Stocks, as they are not listed": non_listed_stocks}