from typing import cast
from app.expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from app.scanner import TokenType


class Interpreter(Visitor[object]):
    def interpret(self, expr: Expr) -> object:
        return expr.accept(self)

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
                return str(val).lower()
            case TokenType.MINUS:
                # TODO: handle runtime errors
                return -right  # type:ignore
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
                return left / right  # type:ignore
        return None

    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def _is_truthy(self, obj: object) -> bool:
        if obj is None or obj == "nil" or obj == "false":
            return False
        return True
