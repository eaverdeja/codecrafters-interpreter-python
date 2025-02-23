from unittest.mock import MagicMock
from app.expr import Expr
from app.interpreter import Interpreter
from app.parser import Parser
from app.scanner import Scanner


class TestInterpreter:
    def generate_expression(self, source: str) -> Expr:
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()
        expr = Parser(tokens, error_reporter=MagicMock()).parse()
        assert expr is not None
        return expr

    def test_can_interpret_boolean_expressions(self):
        expr = self.generate_expression("true")

        res = Interpreter().interpret(expr)

        assert res == "true"

    def test_can_interpret_nil(self):
        expr = self.generate_expression("nil")

        res = Interpreter().interpret(expr)

        assert res == "nil"
