from typing import Literal

class Conversation:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role: Literal["user", "system", "assistant"], content: str):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)