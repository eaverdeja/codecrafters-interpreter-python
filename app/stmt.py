from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.scanner import Token
from app.expr import Expr

R = TypeVar("R")


class Visitor(Generic[R]):
    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> R: ...

    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> R: ...

    @abstractmethod
    def visit_function_stmt(self, stmt: "Function") -> R: ...

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> R: ...

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> R: ...

    @abstractmethod
    def visit_return_stmt(self, stmt: "Return") -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> R: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]): ...


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_block_stmt(self)


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_function_stmt(self)


@dataclass(frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_if_stmt(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_while_stmt(self)


@dataclass(frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_return_stmt(self)


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_var_stmt(self)
