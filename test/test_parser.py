from unittest.mock import MagicMock
from app.expr import Binary, Literal
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType


class TestParser:
    def test_parses_boolen_expressions(self):
        tokens = Scanner(
            source="true != false", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens).parse()

        assert expr == Binary(
            left=Literal(value=True),
            operator=Token(
                token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1
            ),
            right=Literal(value=False),
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
