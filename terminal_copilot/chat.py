from openai import OpenAI
from terminal_copilot.message_util import MessageCreator
from abc import ABC, abstractmethod


class AbstractChatQuerier(ABC):
    @abstractmethod
    def query(self, message: str, histories: list[dict[str, str]]) -> str:
        """
        histories: example: [{"role": "user", "content": "hello"}]
        """
        pass


class OpenAIChatQuerier(AbstractChatQuerier):
    def __init__(self, client: OpenAI, model="gpt-3.5-turbo"):
        self.client = client
        self.model = model

    @staticmethod
    def _from_chat_message(message: dict[str, str]):
        # Currently, it just returns the message as it is
        return message

    @staticmethod
    def _to_chat_message(message: dict[str, str]):
        # Currently, it just returns the message as it is
        return message

    def query(self, message, histories) -> str:
        _messages = histories + [MessageCreator.user(message)]
        messages = [self._from_chat_message(m) for m in _messages]

        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        common_messages = [self._to_chat_message(m) for m in messages]
        return common_messages + [
            MessageCreator.assistant(res.choices[0].message.content)
        ]
