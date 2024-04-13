from dataclasses import dataclass
from enum import Enum


class ChatRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: ChatRole
    content: str

    @staticmethod
    def user(message: str):
        return ChatMessage(ChatRole.USER, message)

    @staticmethod
    def assistant(message: str):
        return ChatMessage(ChatRole.ASSISTANT, message)

    def to_dict(self):
        return {"role": self.role.value, "content": self.content}

    def to_string(self):
        return f"{self.role.value}: {self.content}"
