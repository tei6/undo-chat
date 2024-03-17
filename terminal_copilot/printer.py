from rich.console import Console
from rich.markdown import Markdown
from abc import ABC, abstractmethod


class AbstractResultPrinter(ABC):
    @abstractmethod
    def print(self, text: str):
        pass


class SimplePrinter(AbstractResultPrinter):
    def print(self, text: str):
        print(text)


class MarkdownPrinter(AbstractResultPrinter):
    def __init__(self):
        self.console = Console()

    def print(self, text: str):
        markdown = Markdown(text)
        self.console.print(markdown)
