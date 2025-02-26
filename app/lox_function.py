from dataclasses import dataclass
from app.environment import Environment
from app.lox_callable import LoxCallable
from app.returner import Return
from app.stmt import Function


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function
    closure: Environment

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments) -> None:
        environment = Environment(enclosing=self.closure)
        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except Return as r:
            return r.value

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
