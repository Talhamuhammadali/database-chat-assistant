from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from app.llamaIndex.llamaIndexAgent import ask
from app.chat_bot import ask_lang
from app.langchainService.sql_agent_graph import adaptive_agent
from typing import Optional, List

app = FastAPI(
    title="Assistant-api"
)

class userInput(BaseModel):
    question: str
    chat_history: Optional[list]
    
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/ask")
async def ask_llama(request: userInput):
    response = ask(query=request.question)
    return response


@app.post("/ask/lang")
async def ask_llama(request: userInput):
    response = ask_lang(query=request.question)
    return response["output"]


@app.post("/ask/agent")
async def ask_llama(request: userInput):
    response = adaptive_agent(
        user_question=request.question,
        chat_history=request.chat_history
    )
    return response


@app.post("/summrize")
async def summarize(docs: List[str]):
    summery = docs
    return summery