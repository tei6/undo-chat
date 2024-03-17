import logging
import argparse

from pathlib import Path
from openai import OpenAI
from terminal_copilot.completer import OpenAIQuestionCompleter
from terminal_copilot.chat import AbstractChatQuerier, OpenAIChatQuerier
from terminal_copilot.prompt import AbstractPrompt, PromptToolkitPrompt
from terminal_copilot.printer import AbstractResultPrinter, SimplePrinter
from terminal_copilot.history import AbstractHistoryManager, FileHistoryManager
from terminal_copilot.message_util import MessageCreator

logging.basicConfig(level=logging.INFO, filename="terminal_copilot.log")
logger = logging.getLogger(__name__)


def chat(
    prompt: AbstractPrompt,
    querier: AbstractChatQuerier,
    printer: AbstractResultPrinter,
    history_manager: AbstractHistoryManager,
):
    histories = history_manager.read()
    while True:
        try:
            text = prompt.prompt("> ")
            history_manager.append_history(MessageCreator.user(text))
            histories = querier.query(text, histories)
            message = histories[-1]
            printer.print(message["content"])
            history_manager.append_history(MessageCreator.assistant(message["content"]))

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


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

    message_id = args.message_id
    history_manager = FileHistoryManager(Path("~/chat_history"), message_id)

    client = OpenAI()
    querier = OpenAIChatQuerier(client)
    completer = OpenAIQuestionCompleter(client)
    prompt = PromptToolkitPrompt(completer)
    printer = SimplePrinter()
    chat(prompt, querier, printer, history_manager)


if __name__ == "__main__":
    main()
