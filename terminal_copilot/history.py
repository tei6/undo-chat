from abc import ABC, abstractmethod
from pathlib import Path
import json
from typing import Optional
import copy
import uuid
import datetime


class AbstractHistoryManager(ABC):
    @abstractmethod
    def read(self, message_id: str):
        pass

    @abstractmethod
    def append_history(self, message: dict[str, str]):
        """
        message: a dictionary containing 'role' and 'content'
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


class FileHistoryManager(AbstractHistoryManager):
    def __init__(self, history_dir: Path, message_id: str | None = None):
        history_dir = history_dir.expanduser()
        history_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = history_dir / "history.jsonl"

        histories = []
        if message_id is not None and self.filepath.exists():
            with open(self.filepath, "r") as file:
                for line in file:
                    data = json.loads(line)
                    histories.append(data)
            # It may be better not to filter anything related to message_id here
            histories = self._trace_history(message_id, histories, [])
        self.histories = sorted(histories, key=lambda x: x["updated_at"])

    def _find_history(
        self, message_id: str, histories: list[dict[str, dict]]
    ) -> Optional[dict]:
        for history in histories:
            if history["message_id"] == message_id:
                return history

    def _trace_history(
        self, message_id: str, histories: dict[str, dict], history_chain: list
    ):
        current_history = self._find_history(message_id, histories)
        if current_history:
            history_chain.append(current_history)
            if current_history["parent_message_id"]:
                self._trace_history(
                    current_history["parent_message_id"], histories, history_chain
                )
        return history_chain

    def read(self):
        return [
            {"role": history["role"], "content": history["content"]}
            for history in self.histories
        ]

    def append_history(self, message: dict[str, str]):
        _message = self._to_history(
            message,
            self.histories[-1]["message_id"] if len(self.histories) >= 1 else None,
        )
        with open(self.filepath, "a") as file:
            json_str = json.dumps(_message, ensure_ascii=False)
            file.write(json_str + "\n")

        self.histories.append(_message)
