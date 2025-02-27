from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.scanner import Token

R = TypeVar("R")


class Visitor(Generic[R]):
    @abstractmethod
    def visit_assign_expr(self, expr: "Assign") -> R: ...

    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> R: ...

    @abstractmethod
    def visit_call_expr(self, expr: "Call") -> R: ...

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> R: ...

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> R: ...

    @abstractmethod
    def visit_logical_expr(self, expr: "Logical") -> R: ...

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> R: ...

    @abstractmethod
    def visit_variable_expr(self, expr: "Variable") -> R: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]): ...


@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_assign_expr(self)


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_call_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: object

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True)
class Variable(Expr):
    name: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_variable_expr(self)
