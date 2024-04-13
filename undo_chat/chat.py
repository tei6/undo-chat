from openai import OpenAI
from undo_chat.chat_message import ChatMessage
from abc import ABC, abstractmethod


class AbstractChatQuerier(ABC):
    @abstractmethod
    def query(self, message: str, past_messages: list[ChatMessage]) -> ChatMessage:
        pass


class OpenAIChatQuerier(AbstractChatQuerier):
    def __init__(
        self,
        client: OpenAI,
        model="gpt-3.5-turbo",
    ):
        self.client = client
        self.model = model

    @staticmethod
    def _from_chat_message(message: ChatMessage):
        return {"role": message.role.value, "content": message.content}

    def query(self, message: str, past_messages: list[ChatMessage]) -> ChatMessage:
        _messages = past_messages + [ChatMessage.user(message)]
        messages = [self._from_chat_message(m) for m in _messages]

        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        content = res.choices[0].message.content
        _content = content if type(content) == str else ""
        return ChatMessage.assistant(_content)
