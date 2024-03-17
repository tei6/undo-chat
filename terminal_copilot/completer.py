from abc import ABC, abstractmethod
from openai import OpenAI
import json
from typing import Callable
import textwrap


class MessageCompleter(ABC):
    @abstractmethod
    def completion(self, client, text):
        pass


class OpenAIQuestionCompleter(MessageCompleter):
    def __init__(
        self,
        client: OpenAI,
        model="gpt-3.5-turbo",
        prompt: Callable[[str], str] | None = None,
    ):
        """
        prompt: A function that takes conversation context and creates a prompt
        """

        self.client = client
        self.model = model
        if prompt is not None:
            self._prompt = prompt
        else:
            prompt_str = """
            Below is the conversation between User and Assistant:
            {context}
            
            ---
            Here, the last question from the User is incomplete. Please predict the continuation of the question within 30 characters. It is acceptable if the sentence is cut off.
            Predict three "continuations of the question" and provide the answer as a JSON format with 'messages' as the key and a list of question texts as the value.
            Please match the answer with the language of the question asked.
            """
            prompt_str = textwrap.dedent(prompt_str).strip()
            prompt = lambda context: prompt_str.format(context=context)
        self.prompt = prompt

    def completion(self, text: str, context: list[str] | None = None) -> list[str]:
        if context is None:
            context = []

        content = self.prompt(f"User: {text}")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
        )
        json_str = completion.choices[0].message.content
        json_object = json.loads(json_str)
        return json_object["messages"]
