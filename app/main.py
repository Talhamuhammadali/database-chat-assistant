from fastapi import FastAPI
import uvicorn
# from app.utils.connections import check_database_connection
from app.llamaIndex.llamaIndexAgent import ask
app = FastAPI(
    title="Assistant-api"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ask")
async def ask_llama():
    question = "what are the not public projects being worked on in our company this month.Donot provide details other the what is retrieved from db. Today: 17-05-2024"
    response = ask(query=question)
    return {"message": response}

# docker uncomment as it uses gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)