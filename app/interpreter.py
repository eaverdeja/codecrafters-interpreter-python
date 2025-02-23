from app.expr import Expr, Grouping, Literal, Visitor


class Interpreter(Visitor[object]):
    def interpret(self, expr: Expr) -> object:
        return expr.accept(self)

    def visit_literal_expr(self, expr: Literal) -> object:
        if isinstance(expr.value, float) and expr.value.is_integer():
            return int(expr.value)
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_binary_expr(self, expr): ...
    def visit_unary_expr(self, expr): ...

    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)
