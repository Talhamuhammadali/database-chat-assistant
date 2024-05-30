from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from app.llamaIndex.llamaIndexAgent import ask

app = FastAPI(
    title="Assistant-api"
)

class userInput(BaseModel):
    question: str
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/ask")
async def ask_llama(request: userInput):
    response = ask(query=request.question)
    return {"message": response}
