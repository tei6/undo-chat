from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Optional
import copy
import uuid
import datetime
import copy


class AbstractHistoryMessage(ABC):
    @abstractmethod
    def message(self) -> dict:
        pass

    @abstractmethod
    def parent(self) -> AbstractHistoryMessage:
        pass

    @abstractmethod
    def children(self) -> list[AbstractHistoryMessage]:
        pass


class AbstractHistoryManager(ABC):
    @abstractmethod
    def current_message(self) -> AbstractHistoryMessage:
        pass

    @abstractmethod
    def get_messages(self) -> list[dict]:
        pass

    @abstractmethod
    def read(self) -> list[AbstractHistoryMessage]:
        pass

    @abstractmethod
    def append(self, message: dict[str, str]):
        """
        Add history to the current conversation.
        message: a dictionary containing 'role' and 'content'
        """
        pass

    @abstractmethod
    def undo(self) -> AbstractHistoryMessage | None:
        """
        Go back one level in the history."
        """
        pass

    @staticmethod
    def _to_history(message: dict, parent_message_id: str | None = None):
        _message = copy.copy(message)
        _message.update(
            {
                "message_id": str(uuid.uuid4()),
                "parent_message_id": parent_message_id,
                "updated_at": datetime.datetime.now().isoformat(),
            }
        )
        return _message


class FileHistoryMessage(AbstractHistoryMessage):
    def __init__(self, message: dict, parent=None):
        self._message = message
        self._parent = parent
        self._children: list[FileHistoryMessage] = []

    @property
    def message(self) -> dict:
        return self._message

    @property
    def parent(self) -> Optional[FileHistoryMessage]:
        return self._parent

    def set_parent(self, parent: FileHistoryMessage):
        self._parent = parent

    @property
    def children(self) -> list[FileHistoryMessage]:
        return copy.copy(self._children)

    def add_child(self, child: FileHistoryMessage):
        self._children.append(child)


class FileHistoryManager(AbstractHistoryManager):
    def __init__(self, history_dir: Path):
        history_dir = history_dir.expanduser()
        history_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = history_dir / "history.jsonl"
        self.histories = []
        self.current: FileHistoryMessage | None = None

    def current_message(self) -> FileHistoryMessage:
        return self.current

    def get_messages(self) -> list[dict]:
        history = self.current_message()
        if history is None:
            return []

        messages = [history.message]
        while (history := history.parent) is not None:
            message = history.message
            messages.append(message)

        return messages[::-1]

    def read(self) -> list[FileHistoryMessage]:
        raise NotImplementedError()

    def undo(self) -> FileHistoryMessage | None:
        if self.current:
            self.current = self.current.parent
            return self.current
        else:
            return None

    def append(self, message: dict[str, str]):
        _message = self._to_history(
            message,
            self.histories[-1]["message_id"] if len(self.histories) >= 1 else None,
        )
        self.histories.append(_message)
        if self.current is None:
            self.current = FileHistoryMessage(message=_message)
        else:
            new_message = FileHistoryMessage(message=_message, parent=self.current)
            self.current.add_child(new_message)
            new_message.set_parent(self.current)
            self.current = new_message

        with open(self.filepath, "a") as file:
            json_str = json.dumps(_message, ensure_ascii=False)
            file.write(json_str + "\n")
