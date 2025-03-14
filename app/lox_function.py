from typing import TYPE_CHECKING
from dataclasses import dataclass

from app.environment import Environment
from app.lox_callable import LoxCallable
from app.lox_instance import LoxInstance
from app.returner import Return
from app.stmt import Function

if TYPE_CHECKING:
    from app.interpreter import Interpreter


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function
    closure: Environment
    is_initializer: bool

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(
        self, interpreter: "Interpreter", arguments: list[object]
    ) -> object | None:
        environment = Environment(enclosing=self.closure)
        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except Return as r:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return r.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def bind(self, instance: LoxInstance) -> "LoxFunction":
        environment = Environment(enclosing=self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
