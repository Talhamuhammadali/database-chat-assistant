from fastapi import FastAPI
from app.utils.connections import check_database_connection
from app.langchainService.langchainAgent import test
app = FastAPI(
    title="Assistant-api"
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/connect_db")
async def root():
    status = check_database_connection()

    return {"message": status}

@app.get("/test")
async def root():
    resp = test()

    return {"message": resp}