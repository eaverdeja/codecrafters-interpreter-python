from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction
from app.lox_instance import LoxInstance

if TYPE_CHECKING:
    from app.interpreter import Interpreter


@dataclass
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction]

    def call(self, interpreter: "Interpreter", arguments: list[object]):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0

    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]

    def __str__(self) -> str:
        return self.name
