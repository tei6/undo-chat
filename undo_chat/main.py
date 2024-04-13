import logging
import argparse

from pathlib import Path
from openai import OpenAI
from undo_chat.chat import AbstractChatQuerier, OpenAIChatQuerier
from undo_chat.prompt import (
    AbstractPrompt,
    PromptToolkitPrompt,
    AbstractStateProvider,
)
from undo_chat.printer import AbstractResultPrinter, SimplePrinter
from undo_chat.history import AbstractHistoryManager, FileHistoryManager
from undo_chat.chat_message import ChatMessage

logging.basicConfig(level=logging.INFO, filename="undo_tree.log")
logger = logging.getLogger(__name__)


def chat(
    prompt: AbstractPrompt,
    querier: AbstractChatQuerier,
    printer: AbstractResultPrinter,
    history_manager: AbstractHistoryManager,
):
    while True:
        try:
            past_messages = history_manager.get_messages()
            text = prompt.prompt("> ")
            history_manager.append(ChatMessage.user(text))
            message = querier.query(text, past_messages)
            printer.print(message.content)
            history_manager.append(message)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


class LastQAStateProvider(AbstractStateProvider):
    def __init__(self, history_manager: AbstractHistoryManager) -> None:
        self.history_manager = history_manager
        self._answer: str | None = None
        self._prompt: str | None = None

    def pre_action(self) -> None:
        message = self.history_manager.undo()
        self._prompt = message.get_message().content if message is not None else ""
        message = self.history_manager.undo()
        self._answer = message.get_message().content if message is not None else ""

        return None

    def answer(self) -> str | None:
        return self._answer

    def prompt(self) -> str | None:
        return self._prompt


def parse_args():
    parser = argparse.ArgumentParser(description="Undo Chat")
    return parser.parse_args()


def main():
    _ = parse_args()

    history_manager = FileHistoryManager(Path("~/chat_history"))

    client = OpenAI()
    querier = OpenAIChatQuerier(client)
    prompt = PromptToolkitPrompt(state_provider=LastQAStateProvider(history_manager))
    printer = SimplePrinter()

    chat(
        prompt=prompt, querier=querier, printer=printer, history_manager=history_manager
    )


if __name__ == "__main__":
    main()
