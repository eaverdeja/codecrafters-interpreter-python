from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.lox_callable import LoxCallable
from app.lox_instance import LoxInstance

if TYPE_CHECKING:
    from app.interpreter import Interpreter


@dataclass
class LoxClass(LoxCallable):
    name: str

    def call(self, interpreter: "Interpreter", arguments: list[object]):
        return LoxInstance(self)

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return self.name
