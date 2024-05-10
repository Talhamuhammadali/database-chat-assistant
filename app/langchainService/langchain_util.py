from typing import Literal
from langchain.pydantic_v1 import BaseModel, Field, validator
class Conversation:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role: Literal["user", "system", "assistant"], content: str):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)


class GenerateQuery(BaseModel):
    """Model for inpit arguments of generate query function"""
    user: str = Field(description="The users questions in natural language.")


class ExecutreQuery(BaseModel):
    """Model for input arguments of generate query function"""
    queries: str = Field(description="The query generated by SQL genration LLM")
    

class KnowledgeBase(BaseModel):
    current_goal: str = Field(description="The current task that the user requires you to perform.")
    summery: str = Field(description="Discussion Summery of the conversation.")
    open_problems: str = Field(description="Current problem you are facing that is required to solve user question.")
    

