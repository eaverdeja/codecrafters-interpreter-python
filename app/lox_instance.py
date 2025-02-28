from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.exceptions import RuntimeException
from app.scanner import Token

if TYPE_CHECKING:
    from app.lox_class import LoxClass


@dataclass
class LoxInstance:
    klass: "LoxClass"

    _fields: dict[str, object] = field(default_factory=dict)

    def get(self, token: Token) -> object:
        if token.lexeme not in self._fields:
            raise RuntimeException(token, f"Undefined property {token.lexeme}.")

        return self._fields[token.lexeme]

    def set(self, token: Token, value: object) -> None:
        self._fields[token.lexeme] = value

    def __str__(self):
        return f"{self.klass} instance"
