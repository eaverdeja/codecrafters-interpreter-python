from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def call(self, interpreter: "Interpreter", arguments: list[object]): ...
