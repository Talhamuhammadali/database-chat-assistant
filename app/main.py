from fastapi import FastAPI
import uvicorn
# from app.utils.connections import check_database_connection
from app.langchainService.langchainAgent import test
app = FastAPI(
    title="Assistant-api"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/connect_db")
# async def root():
#     status = check_database_connection()

#     return {"message": status}

@app.get("/ask")
async def root():
    resp = test()
    return {"message": resp}

# docker uncomment as it uses gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)