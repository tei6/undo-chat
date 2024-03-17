class MessageCreator:
    @staticmethod
    def user(message: str):
        return {"role": "user", "content": message}

    @staticmethod
    def assistant(message: str):
        return {"role": "assistant", "content": message}
