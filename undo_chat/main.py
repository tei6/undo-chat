import logging
import argparse

from pathlib import Path
from openai import OpenAI
from undo_chat.completer import OpenAIQuestionCompleter
from undo_chat.chat import AbstractChatQuerier, OpenAIChatQuerier
from undo_chat.prompt import (
    AbstractPrompt,
    PromptToolkitPrompt,
    AbstractStateProvider,
)
from undo_chat.printer import AbstractResultPrinter, SimplePrinter
from undo_chat.history import AbstractHistoryManager, FileHistoryManager
from undo_chat.message_util import MessageCreator

logging.basicConfig(level=logging.INFO, filename="terminal_copilot.log")
logger = logging.getLogger(__name__)


def chat(
    prompt: AbstractPrompt,
    querier: AbstractChatQuerier,
    printer: AbstractResultPrinter,
    history_manager: AbstractHistoryManager,
):
    while True:
        try:
            text = prompt.prompt("> ")
            history_manager.append(MessageCreator.user(text))
            message = querier.query(text)
            printer.print(message["content"])
            history_manager.append(MessageCreator.assistant(message["content"]))

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


class LastQAStateProvider(AbstractStateProvider):
    def __init__(self, history_manager: AbstractHistoryManager) -> None:
        self.history_manager = history_manager
        self._answer = None
        self._prompt = None

    def pre_action(self) -> None:
        message = self.history_manager.undo()
        message_dict = message.message
        self._prompt = message_dict["content"]
        message = self.history_manager.undo()
        message_dict = message.message
        self._answer = message_dict["content"]

        return None

    def answer(self) -> str:
        return self._answer

    def prompt(self) -> str:
        return self._prompt


def parse_args():
    parser = argparse.ArgumentParser(description="Terminal Copilot")
    parser.add_argument(
        "--message-id",
        type=str,
        help="The message ID to start the conversation from",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # message_id = args.message_id
    history_manager = FileHistoryManager(Path("~/chat_history"))

    client = OpenAI()
    querier = OpenAIChatQuerier(client, history_manager=history_manager)
    completer = OpenAIQuestionCompleter(client)
    state_provider = LastQAStateProvider(history_manager)
    prompt = PromptToolkitPrompt(completer, state_provider=state_provider)
    printer = SimplePrinter()

    chat(
        prompt=prompt, querier=querier, printer=printer, history_manager=history_manager
    )


if __name__ == "__main__":
    main()
