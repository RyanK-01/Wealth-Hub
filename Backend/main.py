from fastapi import FastAPI
from Backend.routers import user, finance

app = FastAPI()

#Attach the separate files to the main app
app.include_router(user.routers)
app.include_router(finance.routers)

@app.get("/")
async def root():
    return {"Message": "Welcome to Wealth Hub"}