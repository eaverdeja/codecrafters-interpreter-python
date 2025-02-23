from typing import Callable, TypeGuard
from dataclasses import dataclass

from app.expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from app.scanner import Token, TokenType


class RuntimeException(RuntimeError):
    token: Token

    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


@dataclass
class Interpreter(Visitor[object]):
    error_reporter: Callable[..., None]

    def interpret(self, expr: Expr) -> str | None:
        try:
            val = self._evaluate(expr)
            return self._stringify(val)
        except RuntimeException as e:
            self.error_reporter(e)
            return None

    def visit_literal_expr(self, expr: Literal) -> object:
        if isinstance(expr.value, float) and expr.value.is_integer():
            return int(expr.value)
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                val = not self._is_truthy(right)
                return self._to_lox_bool(val)
            case TokenType.MINUS:
                if self._check_number_operand(right, expr.operator):
                    return -right
                # unreachable
        return None

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            # TODO: handle runtime errors
            case TokenType.PLUS:
                return left + right  # type:ignore
            case TokenType.MINUS:
                return left - right  # type:ignore
            case TokenType.STAR:
                return left * right  # type:ignore
            case TokenType.SLASH:
                val = left / right  # type:ignore
                if val.is_integer():
                    return int(val)
                return val  # type:ignore
            case TokenType.GREATER:
                return self._to_lox_bool(left > right)  # type:ignore
            case TokenType.GREATER_EQUAL:
                return self._to_lox_bool(left >= right)  # type:ignore
            case TokenType.LESS:
                return self._to_lox_bool(left < right)  # type:ignore
            case TokenType.LESS_EQUAL:
                return self._to_lox_bool(left <= right)  # type:ignore
            case TokenType.BANG_EQUAL:
                return self._to_lox_bool(left != right)  # type:ignore
            case TokenType.EQUAL_EQUAL:
                return self._to_lox_bool(left == right)  # type:ignore
        return None

    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def _is_truthy(self, obj: object) -> bool:
        if obj is None or obj == "nil" or obj == "false":
            return False
        return True

    def _to_lox_bool(self, val: bool) -> str:
        return str(val).lower()

    def _stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"
        return str(obj)

    def _check_number_operand(
        self, operand: object, operator: Token
    ) -> TypeGuard[int | float]:
        if isinstance(operand, (int, float)):
            return True
        raise RuntimeException(operator, "Operand must be a number.")
