from openai import OpenAI
from undo_chat.message_util import MessageCreator
from undo_chat.history import AbstractHistoryManager
from abc import ABC, abstractmethod


class AbstractChatQuerier(ABC):
    @abstractmethod
    def query(self, message: str) -> str:
        """
        histories: example: [{"role": "user", "content": "hello"}]
        """
        pass


class OpenAIChatQuerier(AbstractChatQuerier):
    def __init__(
        self,
        client: OpenAI,
        model="gpt-3.5-turbo",
        history_manager: AbstractHistoryManager = None,
    ):
        self.client = client
        self.model = model
        self.history_manager = history_manager

    @staticmethod
    def _from_chat_message(message: dict[str, str]):
        # Currently, it just returns the message as it is
        return {"role": message["role"], "content": message["content"]}

    def query(self, message) -> str:
        messages = self.history_manager.get_messages()
        _messages = messages + [MessageCreator.user(message)]
        messages = [self._from_chat_message(m) for m in _messages]

        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        return MessageCreator.assistant(res.choices[0].message.content)
