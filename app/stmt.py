from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.scanner import Token

R = TypeVar("R")


class Visitor(Generic[R]):
    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> R: ...

    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> R: ...

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> R: ...

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> R: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]): ...


@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_block_stmt(self)


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_if_stmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_print_stmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_while_stmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_var_stmt(self)
