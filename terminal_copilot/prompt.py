from abc import ABC, abstractmethod
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from terminal_copilot.completer import MessageCompleter


class AbstractStateProvider(ABC):
    @abstractmethod
    def pre_action(self) -> str:
        pass

    @abstractmethod
    def answer(self) -> str:
        pass

    @abstractmethod
    def prompt(self) -> str:
        pass


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
    def __init__(
        self,
        completer: MessageCompleter = None,
        state_provider: AbstractStateProvider = None,
    ):
        if completer is None:
            self.session = PromptSession()
        else:
            self.session = PromptSession(
                completer=PromptToolkitPromptCompleter(completer)
            )

        self.bindings = self._get_bindings(state_provider)

    def _get_bindings(self, provider: AbstractStateProvider | None):
        if provider is None:
            return None

        bindings = KeyBindings()

        @bindings.add("c-t")
        def _(event):
            provider.pre_action()

            def print_pre_message():
                print("-----")
                message = provider.answer()
                print(message)

            run_in_terminal(print_pre_message)
            buffer = event.app.current_buffer
            buffer.text = provider.prompt()

        return bindings

    def prompt(self, text: str):
        # Setting complete_while_typing=False improves the interaction between automatic completion and manual completion, so it is temporarily set to False.
        return self.session.prompt(
            text, complete_while_typing=False, key_bindings=self.bindings
        )
