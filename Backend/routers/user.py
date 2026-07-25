import os
import hashlib
import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime, timedelta, timezone

#Auto adds "/user" to all endpoints in this file
routers = APIRouter(prefix="/user", tags=["User"])

#Variable List
acc_list=[]

#Models
class account(BaseModel):
    username: str
    password: str

class acc_details(BaseModel):
    pass

#The URL the frontend should use to get a token
load_dotenv()
secret = os.getenv("SECRET_KEY")
if not secret:
    raise ValueError("No SECRET_KEY set for FastAPI application. Check your .env file!")
Algo = "HS256"
Access_Token_Expire_Min = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    
    #Calculate expiration time based on my variable
    expire = datetime.now(timezone.utc) + timedelta(minutes=Access_Token_Expire_Min)
    to_encode.update({"expire": expire})
    
    #Generate the cryptographic string
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=Algo)
    
    return encoded_jwt

#Get current username
def get_curr_user(token: Annotated[str, Depends(oauth2_scheme)]):
    #Standard security exception to throw if anything goes wrong
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Decode the JWT using your secret key
        payload = jwt.decode(token, secret, algorithms=[Algo])
        
        #Extract the username from the "sub" field
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    #Catch errors if the token is expired or tampered with
    except jwt.PyJWTError:
        raise credentials_exception
        
    #Find the matching user in your database
    for user in acc_list:
        if user["username"] == username:
            return user
            
    #If token is valid but user no longer exists in the list
    raise credentials_exception

#Register user
@routers.post("/register", status_code=status.HTTP_201_CREATED)
def register_acc(acc: account):
    acc_dict = acc.dict()
    raw_pw = acc_dict["password"].encode('utf-8')
    sha256_bytes = hashlib.sha256(raw_pw).hexdigest().encode('utf-8')
    pwd_hashed = bcrypt.hashpw(sha256_bytes, bcrypt.gensalt())
    acc_dict["password"] = pwd_hashed.decode('utf-8')
    acc_list.append(acc_dict)
    return {"Status": "Success", "Account Detail": acc_dict}

#Login
@routers.post("/login")
def login(data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    matched_user=None
    for scope in acc_list:
        if data.username == scope["username"]:
            matched_user = scope
            break
    
    #Username is not found in DB
    if matched_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    login_pw_bytes = data.password.encode('utf-8')
    login_sha256_bytes = hashlib.sha256(login_pw_bytes).hexdigest().encode('utf-8')
    matched_pw = matched_user["password"].encode('utf-8')
    
    #Verify password
    if bcrypt.checkpw(login_sha256_bytes, matched_pw):
        access_token = create_access_token(data={"sub": matched_user["username"]})
        return {"Status": "Success", "Access Token": access_token}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

#Get User account
@routers.get("/me")
def get_account(curr_user: Annotated[dict, Depends(get_curr_user)]):
    return {"Status": "Success", "Account Details": curr_user}