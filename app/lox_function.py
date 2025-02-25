from dataclasses import dataclass
from app.lox_callable import LoxCallable
from app.stmt import Function


@dataclass
class LoxFunction(LoxCallable):
    declaration: Function

    def call(self, interpreter, arguments) -> None:
        interpreter._execute_block(self.declaration.body, interpreter._globals)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
