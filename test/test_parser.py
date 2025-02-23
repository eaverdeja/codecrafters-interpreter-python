from unittest.mock import MagicMock
from app.expr import Binary, Grouping, Literal, Unary
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType


class TestParser:
    def test_parses_boolen_expressions(self):
        tokens = Scanner(
            source="true != false", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Literal(value="true"),
            operator=Token(
                token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1
            ),
            right=Literal(value="false"),
        )

    def test_parses_number_literals(self):
        tokens = Scanner(source="42 - 15", error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Literal(value=42.0),
            operator=Token(
                token_type=TokenType.MINUS, lexeme="-", literal=None, line=1
            ),
            right=Literal(value=15.0),
        )

    def test_parses_string_literals(self):
        tokens = Scanner(
            source='"hello world"', error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Literal(value="hello world")

    def test_parses_groups(self):
        tokens = Scanner(source='("foo")', error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Grouping(expression=Literal(value="foo"))

    def test_parses_unary_operators(self):
        tokens = Scanner(source="!!true", error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Unary(
            operator=Token(token_type=TokenType.BANG, lexeme="!", literal=None, line=1),
            right=Unary(
                Token(token_type=TokenType.BANG, lexeme="!", literal=None, line=1),
                right=Literal(value="true"),
            ),
        )

    def test_parses_arithmetic_expressions(self):
        tokens = Scanner(
            source="16 * 38 / 58", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Binary(
                left=Literal(value=16.0),
                operator=Token(
                    token_type=TokenType.STAR, lexeme="*", literal=None, line=1
                ),
                right=Literal(value=38.0),
            ),
            operator=Token(
                token_type=TokenType.SLASH, lexeme="/", literal=None, line=1
            ),
            right=Literal(value=58.0),
        )

    def test_parses_arithmetic_expressions_2(self):
        tokens = Scanner(
            source="52 + 80 - 94", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Binary(
                left=Literal(value=52.0),
                operator=Token(
                    token_type=TokenType.PLUS, lexeme="+", literal=None, line=1
                ),
                right=Literal(value=80.0),
            ),
            operator=Token(
                token_type=TokenType.MINUS, lexeme="-", literal=None, line=1
            ),
            right=Literal(value=94.0),
        )

    def test_parses_comparsion_operators(self):
        tokens = Scanner(
            source="83 < 99 < 115", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Binary(
                left=Literal(value=83.0),
                operator=Token(
                    token_type=TokenType.LESS, lexeme="<", literal=None, line=1
                ),
                right=Literal(value=99.0),
            ),
            operator=Token(token_type=TokenType.LESS, lexeme="<", literal=None, line=1),
            right=Literal(value=115.0),
        )

    def test_parses_equality_operators(self):
        tokens = Scanner(
            source='"baz" == "baz"', error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Literal(value="baz"),
            operator=Token(
                token_type=TokenType.EQUAL_EQUAL, lexeme="==", literal=None, line=1
            ),
            right=Literal(value="baz"),
        )
