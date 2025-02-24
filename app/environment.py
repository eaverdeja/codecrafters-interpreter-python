from dataclasses import dataclass, field
from typing import Self

from app.exceptions import RuntimeException
from app.scanner import Token


@dataclass
class Environment:
    values: dict[str, object] = field(default_factory=dict)
    enclosing: Self | None = None

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme not in self.values:
            raise RuntimeException(name, f"Undefined variable '{name.lexeme}'")
        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        self.values[name.lexeme] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
