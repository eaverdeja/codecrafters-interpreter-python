from typing import Callable, TypeGuard
from dataclasses import dataclass

from app import expr, stmt
from app.stmt import Expression, Print, Stmt
from app.expr import Binary, Expr, Grouping, Literal, Unary
from app.scanner import Token, TokenType


class RuntimeException(RuntimeError):
    token: Token

    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


@dataclass
class Interpreter(expr.Visitor[object], stmt.Visitor[None]):
    error_reporter: Callable[..., None]

    def interpret(self, expr: Expr) -> str | None:
        try:
            val = self._evaluate(expr)
            return self._stringify(val)
        except RuntimeException as e:
            self.error_reporter(e)
            return None

    def interpret_all(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeException as e:
            self.error_reporter(e)

    def visit_literal_expr(self, expr: Literal) -> object:
        if isinstance(expr.value, float) and expr.value.is_integer():
            return int(expr.value)
        if expr.value == "true":
            return True
        if expr.value == "false":
            return False
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                val = not self._is_truthy(right)
                return val
            case TokenType.MINUS:
                if self._check_number_operand(right, expr.operator):
                    return -right
        return None

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise RuntimeException(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right

        if self._check_number_operand(
            left, expr.operator
        ) and self._check_number_operand(right, expr.operator):
            match expr.operator.token_type:
                case TokenType.MINUS:
                    return left - right
                case TokenType.STAR:
                    return left * right
                case TokenType.SLASH:
                    val = left / right
                    if val.is_integer():
                        return int(val)
                    return val
                case TokenType.GREATER:
                    return left > right
                case TokenType.GREATER_EQUAL:
                    return left >= right
                case TokenType.LESS:
                    return left < right
                case TokenType.LESS_EQUAL:
                    return left <= right

        return None

    def visit_print_stmt(self, stmt: Print) -> None:
        val = self._evaluate(stmt.expression)
        print(self._stringify(val))

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def _is_truthy(self, obj: object) -> bool:
        if obj is None or obj == False or obj == "nil":
            return False
        return True

    def _stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"
        if obj is True or obj is False:
            return str(obj).lower()
        return str(obj)

    def _check_number_operand(
        self, operand: object, operator: Token
    ) -> TypeGuard[int | float]:
        # isinstance(True, int) evaluates to True in python :/
        if not isinstance(operand, bool) and isinstance(operand, (int, float)):
            return True
        raise RuntimeException(operator, "Operand must be a number.")
