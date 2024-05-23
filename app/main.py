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
    # question = "what are the not public projects being worked on in our company this month.Donot provide details other the what is retrieved from db. Today: 17-05-2024"
    response = ask(query=request.question)
    print(type(response))
    return {"message": response.response}
