from pydantic import BaseModel
from typing import List, Optional, Dict

class Docs(BaseModel):
    input: List[str]
    running_summaries: List[str]

class userInput(BaseModel):
    question: str
    chat_history: Optional[list]

class summaryResponse(BaseModel):
    response: List[Dict[str, str]]