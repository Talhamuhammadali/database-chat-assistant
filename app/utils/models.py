from pydantic import BaseModel
from typing import List, Optional

class Docs(BaseModel):
    input: List[str]

class userInput(BaseModel):
    question: str
    chat_history: Optional[list]