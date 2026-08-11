from gc import disable
from re import I

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from datetime import date, datetime, timezone
from typing import Optional, Literal
from Backend.routers.user import get_curr_user

#Auto adds "/finance" to all endpoints in this file
routers = APIRouter(prefix="/finance", tags=["Finance"])

transaction_list=[]

#ID counter (For mock data)
def ID_count(transaction_list):
    if not transaction_list:
        return 1
    else:
        return max(t["id"] for t in transaction_list) + 1

#Models
class transaction(BaseModel):
    id: Optional [int]=None
    username: Optional [str]=None
    type: Literal["Income", "Expense"]
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    amount: float
    category: str
    payment: str
    description: Optional [str]=None
    
@routers.post("/transaction")
def create_transaction(trans: transaction, curr_user: dict = Depends(get_curr_user)):
    trans_dict = trans.dict()
    username = curr_user["username"]
    new_id = ID_count(transaction_list)
    trans_dict["id"] = new_id
    trans_dict["username"] = username
    transaction_list.append(trans_dict)
    return {"message": f"Successfully created new transaction (ID: {new_id}) for {username}"}

@routers.get("/transaction/{id}")
def retrieve_transaction(id: int, curr_user: dict = Depends(get_curr_user)):
    for trans in transaction_list:
        if trans["id"] == id:
            if trans["username"] == curr_user["username"]:
                return trans
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this transaction")
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

@routers.put("/transaction/{id}")
def edit_transaction(id: int, trans_update: transaction, curr_user: dict = Depends(get_curr_user)):
    for trans in transaction_list:
        if trans["id"] == id:
            if trans["username"] == curr_user["username"]:
                update_data = trans_update.dict()
                trans["type"] = update_data["type"]
                trans["amount"] = update_data["amount"]
                trans["category"] = update_data["category"]
                trans["payment"] = update_data["payment"]
                trans["description"] = update_data["description"]
                return {"message": "Transaction updated successfully", "transaction": trans}
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this transaction")
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")        

@routers.delete("/transaction/{id}")
def del_transaction(id: int, curr_user: dict = Depends(get_curr_user)):
    for trans in transaction_list:
        if trans["id"] == id:
            if trans["username"] == curr_user["username"]:
                transaction_list.remove(trans)
                return {"message": "Transaction deleted successfully", "transaction": trans}
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this transaction")
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

@routers.get("/transaction")
def list_transation(curr_user: dict = Depends(get_curr_user,
                    )):
    
        
    pass