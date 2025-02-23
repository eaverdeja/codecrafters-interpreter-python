from app.scanner import Token


class RuntimeException(RuntimeError):
    token: Token

    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
