from dataclasses import dataclass
from app.environment import Environment
from app.lox_callable import LoxCallable
from app.stmt import Function


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function

    def call(self, interpreter, arguments) -> None:
        environment = Environment(enclosing=interpreter._globals)
        for i in range(0, len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        interpreter._execute_block(self.declaration.body, environment)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
