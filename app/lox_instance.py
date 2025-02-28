from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.exceptions import RuntimeException
from app.scanner import Token

if TYPE_CHECKING:
    from app.lox_class import LoxClass


@dataclass
class LoxInstance:
    klass: "LoxClass"
    fields: dict[str, object]

    def get(self, token: Token) -> object:
        if token.lexeme not in self.fields:
            raise RuntimeException(token, f"Undefined property {token.lexeme}.")

        return self.fields[token.lexeme]

    def __str__(self):
        return f"{self.klass} instance"
