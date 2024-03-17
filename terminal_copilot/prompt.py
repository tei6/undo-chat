from abc import ABC, abstractmethod
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer
from prompt_toolkit.completion import Completion
from terminal_copilot.completer import MessageCompleter


class AbstractPrompt(ABC):
    @abstractmethod
    def prompt(self, text: str):
        pass


class PromptToolkitPromptCompleter(Completer):
    def __init__(self, completer: MessageCompleter):
        self.completer = completer

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        commands = self.completer.completion(document.text)
        for command in commands:
            # It is still unclear whether it is allowed to replace the original text.
            yield Completion(command, start_position=-len(text))


class PromptToolkitPrompt(AbstractPrompt):
    def __init__(self, completer: MessageCompleter = None):
        if completer is None:
            self.session = PromptSession()
        else:
            self.session = PromptSession(completer=PromptToolkitPromptCompleter(completer))

    def prompt(self, text: str):
        # Setting complete_while_typing=False improves the interaction between automatic completion and manual completion, so it is temporarily set to False.
        return self.session.prompt(text, complete_while_typing=False)
