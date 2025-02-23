from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.scanner import Token
from app.expr import Expr

R = TypeVar("R")


class Visitor(Generic[R]):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> R: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]): ...


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_print_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_var_stmt(self)
