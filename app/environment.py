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
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'")

    def assign_at(self, distance: int, name: Token, val: object) -> None:
        self._ancestor(distance).values[name.lexeme] = val

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> object:
        return self._ancestor(distance).values[name]

    def _ancestor(self, distance: int) -> Self:
        environment = self
        for _ in range(0, distance):
            if not environment.enclosing:
                raise AssertionError(
                    "Could not reach designated environment for variable."
                )
            environment = environment.enclosing
        return environment
