from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal
from Backend.routers.user import get_curr_user, acc_list, account

#Auto adds "/finance" to all endpoints in this file
routers = APIRouter(prefix="/finance", tags=["Finance"])

transaction_list=[]
#ID counter
def ID_count(transaction_list):
    if not transaction_list:
        return 1
    else:
        return max(t["id"] for t in transaction_list) + 1

#Models
class transaction(BaseModel):
    id: Optional [int]=None
    type: Literal["Income", "Expense"]
    date: datetime
    amount: float
    category: str
    payment: str
    description: Optional [str]=None
    
@routers.post("/transaction")
def create_transaction(trans: transaction, curr_user: dict = Depends(get_curr_user)):
    for user in acc_list:
        if user["username"] == curr_user["username"]:
            username = curr_user["username"]
            trans["id"] = ID_count(transaction_list)
            transaction_list.append(trans)
            return {"message": f"Successfully created new transaction for {username}"}
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect autehntication credetials", 
                        headers={"WWW-Authenticate": "Bearer"})

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
                trans["id"] == update_data["id"]
                trans["type"] == update_data["type"]
                trans["date"] == update_data["date"]
                trans["amount"] == update_data["amount"]
                trans["category"] == update_data["category"]
                trans["payment"] == update_data["payment"]
                trans["description"] == update_data["description"]
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
    
    raise HTTPException(status_code=status.HTTP_404_FORBIDDEN, detail="Transaction not found")
