from unittest import mock
from unittest.mock import MagicMock
from app.expr import Expr
from app.interpreter import Interpreter, RuntimeException
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType


class TestInterpreter:
    def generate_expression(self, source: str, should_fail: bool = False) -> Expr:
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()
        expr = Parser(tokens, error_reporter=MagicMock()).parse()
        assert should_fail or expr is not None
        return expr  # type: ignore

    def test_can_interpret_boolean_expressions(self):
        expr = self.generate_expression("true")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "true"

    def test_can_interpret_nil(self):
        expr = self.generate_expression("nil")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "nil"

    def test_can_interpret_integers(self):
        expr = self.generate_expression("42")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "42"

    def test_can_interpret_floating_point_numbers(self):
        expr = self.generate_expression("3.14")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "3.14"

    def test_can_interpret_arbitrary_strings(self):
        expr = self.generate_expression('"foo bar"')

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "foo bar"

    def test_can_interpret_parentheses(self):
        expr = self.generate_expression("((false))")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "false"

    def test_can_interpret_unary_expressions(self):
        expr = self.generate_expression("-42")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "-42"

    def test_can_interpret_unary_expressions_2(self):
        expr = self.generate_expression("!true")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "false"

    def test_can_interpret_arithmetic_expressions(self):
        expr = self.generate_expression("3 * 3 / 2.142857142857143")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "4.2"

    def test_can_interpret_arithmetic_expressions_2(self):
        expr = self.generate_expression("20 + 74 - (-(14 - 33))")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "75"

    def test_can_interpret_concatenated_strings(self):
        expr = self.generate_expression('"hello" + ", world!"')

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "hello, world!"

    def test_can_interpret_relational_operators(self):
        expr = self.generate_expression("42 > 17")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "true"

    def test_can_interpret_equality_operators(self):
        expr = self.generate_expression("156 == (89 + 67)")

        res = Interpreter(error_reporter=MagicMock()).interpret(expr)

        assert res == "true"

    def test_can_report_runtime_errors(self):
        error_reporter = MagicMock()
        expr = self.generate_expression('-"hello"')

        res = Interpreter(error_reporter=error_reporter).interpret(expr)
        assert res is None

        assert len(error_reporter.mock_calls) == 1
        error = error_reporter.call_args[0][0]

        assert type(error) == RuntimeException
        assert str(error) == "Operand must be a number."
        error.token == Token(TokenType.STRING, lexeme="hello", literal=None, line=1)
