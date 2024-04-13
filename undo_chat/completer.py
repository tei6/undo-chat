from abc import ABC, abstractmethod


class MessageCompleter(ABC):
    @abstractmethod
    def completion(self, client, text):
        pass
