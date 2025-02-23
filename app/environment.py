from dataclasses import dataclass, field

from app.exceptions import RuntimeException
from app.scanner import Token


@dataclass
class Environment:
    values: dict[str, object] = field(default_factory=dict)

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
