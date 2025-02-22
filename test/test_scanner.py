from unittest.mock import MagicMock, call
from app.scanner import Scanner, Token, TokenType


class TestScanTokens:
    def test_parentheses(self):
        scanner = Scanner(source="(()", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1),
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1),
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_braces(self):
        scanner = Scanner(source="{}", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.LEFT_BRACE, lexeme="{", literal=None, line=1),
            Token(token_type=TokenType.RIGHT_BRACE, lexeme="}", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_other_single_chars(self):
        scanner = Scanner(source="*.,+;", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=1),
            Token(token_type=TokenType.DOT, lexeme=".", literal=None, line=1),
            Token(token_type=TokenType.COMMA, lexeme=",", literal=None, line=1),
            Token(token_type=TokenType.PLUS, lexeme="+", literal=None, line=1),
            Token(token_type=TokenType.SEMICOLON, lexeme=";", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_one_or_two_chars_lexemes(self):
        scanner = Scanner(source="===<=>!!=>=<", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.EQUAL_EQUAL, lexeme="==", literal=None, line=1),
            Token(token_type=TokenType.EQUAL, lexeme="=", literal=None, line=1),
            Token(token_type=TokenType.LESSER_EQUAL, lexeme="<=", literal=None, line=1),
            Token(token_type=TokenType.GREATER, lexeme=">", literal=None, line=1),
            Token(token_type=TokenType.BANG, lexeme="!", literal=None, line=1),
            Token(token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1),
            Token(
                token_type=TokenType.GREATER_EQUAL, lexeme=">=", literal=None, line=1
            ),
            Token(token_type=TokenType.LESSER, lexeme="<", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_lexical_errors(self):
        error_reporter = MagicMock()
        scanner = Scanner(source="%$-", error_reporter=error_reporter)

        tokens = scanner.scan_tokens()

        error_reporter.assert_has_calls(
            [call(1, "Unexpected character: %")], [call(1, "Unexpected character: $")]
        )

        assert tokens == [
            Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]
