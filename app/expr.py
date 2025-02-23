from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from app.scanner import Token

R = TypeVar("R")


class Visitor(Generic[R]):
    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> R: ...

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> R: ...

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> R: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]): ...


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_binary_expr(self)


@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_literal_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_unary_expr(self)
