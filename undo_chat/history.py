from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Optional, TypeVar, Generic, Any
import copy
import uuid
import datetime
import copy
from undo_chat.chat_message import ChatMessage, ChatRole

T = TypeVar("T", bound="AbstractHistory")


class AbstractHistory(ABC, Generic[T]):
    @abstractmethod
    def get_message(self) -> ChatMessage:
        pass

    @abstractmethod
    def get_parent(self) -> AbstractHistory | None:
        pass

    @abstractmethod
    def get_children(self) -> list[T]:
        pass


class AbstractHistoryManager(ABC):
    @abstractmethod
    def current_message(self) -> AbstractHistory | None:
        pass

    @abstractmethod
    def get_messages(self) -> list[ChatMessage]:
        pass

    @abstractmethod
    def read(self) -> list[AbstractHistory]:
        pass

    @abstractmethod
    def append(self, message: ChatMessage):
        """
        Add history to the current conversation.
        message: a dictionary containing 'role' and 'content'
        """
        pass

    @abstractmethod
    def undo(self) -> AbstractHistory | None:
        """
        Go back one level in the history."
        """
        pass

    @staticmethod
    def _to_history(message: ChatMessage, parent_message_id: str | None = None):
        message_dict = message.to_dict()
        _message = copy.copy(message_dict)
        _message.update(
            {
                "message_id": str(uuid.uuid4()),
                "parent_message_id": parent_message_id,
                "updated_at": datetime.datetime.now().isoformat(),
            }
        )
        return _message


class FileHistoryMessage(AbstractHistory):
    def __init__(self, message: dict, parent=None):
        self._message = message
        self._parent = parent
        self._children: list[FileHistoryMessage] = []

    def get_message(self) -> ChatMessage:
        message = self._message
        role = ChatRole(message["role"])
        content = message["content"]
        return ChatMessage(role, content)

    def get_parent(self) -> Optional[FileHistoryMessage]:
        return self._parent

    def set_parent(self, parent: FileHistoryMessage):
        self._parent = parent

    def get_children(self) -> list[FileHistoryMessage]:
        return copy.copy(self._children)

    def add_child(self, child: FileHistoryMessage):
        self._children.append(child)


class FileHistoryManager(AbstractHistoryManager):
    def __init__(self, history_dir: Path, logfile_name="history.jsonl"):
        history_dir = history_dir.expanduser()
        history_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = history_dir / logfile_name
        self.histories: list[dict[str, Any]] = []
        self.current: FileHistoryMessage | None = None

    def current_message(self) -> FileHistoryMessage | None:
        return self.current

    def get_messages(self) -> list[ChatMessage]:
        history = self.current_message()
        if history is None:
            return []

        messages = [history.get_message()]
        while (history := history.get_parent()) is not None:  # type: ignore
            messages.append(history.get_message())

        return messages[::-1]

    def read(self) -> list[AbstractHistory]:
        raise NotImplementedError()

    def undo(self) -> FileHistoryMessage | None:
        if self.current:
            self.current = self.current.get_parent()
            return self.current
        else:
            return None

    def append(self, message: ChatMessage):
        history_message = self._to_history(
            message,
            self.histories[-1]["message_id"] if len(self.histories) >= 1 else None,
        )
        self.histories.append(history_message)
        if self.current is None:
            self.current = FileHistoryMessage(message=history_message)
        else:
            new_message = FileHistoryMessage(
                message=history_message, parent=self.current
            )
            self.current.add_child(new_message)
            new_message.set_parent(self.current)
            self.current = new_message

        with open(self.filepath, "a") as file:
            json_str = json.dumps(history_message, ensure_ascii=False)
            file.write(json_str + "\n")
