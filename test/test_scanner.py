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
            Token(token_type=TokenType.LESS_EQUAL, lexeme="<=", literal=None, line=1),
            Token(token_type=TokenType.GREATER, lexeme=">", literal=None, line=1),
            Token(token_type=TokenType.BANG, lexeme="!", literal=None, line=1),
            Token(token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1),
            Token(
                token_type=TokenType.GREATER_EQUAL, lexeme=">=", literal=None, line=1
            ),
            Token(token_type=TokenType.LESS, lexeme="<", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_multiline(self):
        source = """
        // this is a comment
        (( )){} // grouping stuff
        !*+-/=<> <= == // operators
        """

        scanner = Scanner(source=source, error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=3),
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=3),
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=3),
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=3),
            Token(token_type=TokenType.LEFT_BRACE, lexeme="{", literal=None, line=3),
            Token(token_type=TokenType.RIGHT_BRACE, lexeme="}", literal=None, line=3),
            Token(token_type=TokenType.BANG, lexeme="!", literal=None, line=4),
            Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=4),
            Token(token_type=TokenType.PLUS, lexeme="+", literal=None, line=4),
            Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=4),
            Token(token_type=TokenType.SLASH, lexeme="/", literal=None, line=4),
            Token(token_type=TokenType.EQUAL, lexeme="=", literal=None, line=4),
            Token(token_type=TokenType.LESS, lexeme="<", literal=None, line=4),
            Token(token_type=TokenType.GREATER, lexeme=">", literal=None, line=4),
            Token(token_type=TokenType.LESS_EQUAL, lexeme="<=", literal=None, line=4),
            Token(token_type=TokenType.EQUAL_EQUAL, lexeme="==", literal=None, line=4),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=5),
        ]

    def test_strings(self):
        source = '("world"+"hello") != "other_string"'
        scanner = Scanner(source=source, error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1),
            Token(
                token_type=TokenType.STRING, lexeme='"world"', literal="world", line=1
            ),
            Token(token_type=TokenType.PLUS, lexeme="+", literal=None, line=1),
            Token(
                token_type=TokenType.STRING, lexeme='"hello"', literal="hello", line=1
            ),
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1),
            Token(token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1),
            Token(
                token_type=TokenType.STRING,
                lexeme='"other_string"',
                literal="other_string",
                line=1,
            ),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_numbers(self):
        scanner = Scanner(source="99.31", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.NUMBER, lexeme="99.31", literal=99.31, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_identifiers(self):
        scanner = Scanner(source="foo bar", error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="bar", literal=None, line=1),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=1),
        ]

    def test_keywords(self):
        source = "IF PRINT class TRUE true false VAR this if FALSE OR RETURN else FUN NIL FOR for print nil and return CLASS THIS var ELSE or SUPER fun super AND while WHILE"
        scanner = Scanner(source=source, error_reporter=MagicMock())

        tokens = scanner.scan_tokens()

        assert tokens == [
            Token(token_type=TokenType.IDENTIFIER, lexeme="IF", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="PRINT", literal=None, line=1
            ),
            Token(token_type=TokenType.CLASS, lexeme="class", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="TRUE", literal=None, line=1),
            Token(token_type=TokenType.TRUE, lexeme="true", literal=None, line=1),
            Token(token_type=TokenType.FALSE, lexeme="false", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="VAR", literal=None, line=1),
            Token(token_type=TokenType.THIS, lexeme="this", literal=None, line=1),
            Token(token_type=TokenType.IF, lexeme="if", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="FALSE", literal=None, line=1
            ),
            Token(token_type=TokenType.IDENTIFIER, lexeme="OR", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="RETURN", literal=None, line=1
            ),
            Token(token_type=TokenType.ELSE, lexeme="else", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="FUN", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="NIL", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="FOR", literal=None, line=1),
            Token(token_type=TokenType.FOR, lexeme="for", literal=None, line=1),
            Token(token_type=TokenType.PRINT, lexeme="print", literal=None, line=1),
            Token(token_type=TokenType.NIL, lexeme="nil", literal=None, line=1),
            Token(token_type=TokenType.AND, lexeme="and", literal=None, line=1),
            Token(token_type=TokenType.RETURN, lexeme="return", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="CLASS", literal=None, line=1
            ),
            Token(token_type=TokenType.IDENTIFIER, lexeme="THIS", literal=None, line=1),
            Token(token_type=TokenType.VAR, lexeme="var", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="ELSE", literal=None, line=1),
            Token(token_type=TokenType.OR, lexeme="or", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="SUPER", literal=None, line=1
            ),
            Token(token_type=TokenType.FUN, lexeme="fun", literal=None, line=1),
            Token(token_type=TokenType.SUPER, lexeme="super", literal=None, line=1),
            Token(token_type=TokenType.IDENTIFIER, lexeme="AND", literal=None, line=1),
            Token(token_type=TokenType.WHILE, lexeme="while", literal=None, line=1),
            Token(
                token_type=TokenType.IDENTIFIER, lexeme="WHILE", literal=None, line=1
            ),
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

    def test_multiline_errors(self):
        source = """# (
        )   @
        """
        error_reporter = MagicMock()
        scanner = Scanner(source=source, error_reporter=error_reporter)

        tokens = scanner.scan_tokens()

        error_reporter.assert_has_calls(
            [call(1, "Unexpected character: #")], [call(2, "Unexpected character: @")]
        )

        assert tokens == [
            Token(token_type=TokenType.LEFT_PAREN, lexeme="(", literal=None, line=1),
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=2),
            Token(token_type=TokenType.EOF, lexeme="", literal=None, line=3),
        ]
