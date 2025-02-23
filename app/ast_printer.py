from app.expr import Binary, Expr, Grouping, Literal, Unary, Visitor
from app.scanner import Token, TokenType


class AstPrinter(Visitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self._parenthisize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self._parenthisize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        if isinstance(expr.value, int):
            return str(float(expr.value))
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self._parenthisize(expr.operator.lexeme, expr.right)

    def _parenthisize(self, name: str, *exprs: Expr) -> str:
        res = f"({name}"
        for expr in exprs:
            res += f" {expr.accept(self)}"
        res += ")"

        return res


def main() -> None:
    # Simple smoke test
    expr: Expr = Binary(
        Literal(2),
        Token(TokenType.PLUS, "+", None, 1),
        Literal(3),
    )

    print(AstPrinter().print(expr))


if __name__ == "__main__":
    main()
