from unittest import mock
from unittest.mock import MagicMock
from app.expr import Assign, Binary, Grouping, Literal, Unary, Variable
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType
from app.stmt import Block, Expression, If, Print, Var


class TestParse:
    def test_parses_boolen_expressions(self):
        tokens = Scanner(
            source="true != false", error_reporter=MagicMock()
        ).scan_tokens()

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

        assert expr == Binary(
            left=Literal(value="true"),
            operator=Token(
                token_type=TokenType.BANG_EQUAL, lexeme="!=", literal=None, line=1
            ),
            right=Literal(value="false"),
        )

    def test_parses_number_literals(self):
        tokens = Scanner(source="42 - 15", error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

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

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

        assert expr == Literal(value="hello world")

    def test_parses_groups(self):
        tokens = Scanner(source='("foo")', error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

        assert expr == Grouping(expression=Literal(value="foo"))

    def test_parses_unary_operators(self):
        tokens = Scanner(source="!!true", error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

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

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

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

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

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

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

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

        expr = Parser(tokens, error_reporter=MagicMock()).parse()

        assert expr == Binary(
            left=Literal(value="baz"),
            operator=Token(
                token_type=TokenType.EQUAL_EQUAL, lexeme="==", literal=None, line=1
            ),
            right=Literal(value="baz"),
        )

    def test_syntatic_errors(self):
        error_reporter = MagicMock()
        tokens = Scanner(source="(42 +)", error_reporter=MagicMock()).scan_tokens()

        expr = Parser(tokens, error_reporter=error_reporter).parse()

        assert expr is None

        error_reporter.assert_called_once_with(
            Token(token_type=TokenType.RIGHT_PAREN, lexeme=")", literal=None, line=1),
            "Expect expression.",
        )


class TestParseAll:
    def test_parses_all_into_statements(self):
        source = """
        'print "foo" + "bar";'
        'print "bar" + "hello" + "quz";'
        """
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Print(
                expression=Binary(
                    left=Literal(value="foo"),
                    operator=Token(
                        token_type=TokenType.PLUS, lexeme="+", literal=None, line=2
                    ),
                    right=Literal(value="bar"),
                )
            ),
            Print(
                expression=Binary(
                    left=Binary(
                        left=Literal(value="bar"),
                        operator=Token(
                            token_type=TokenType.PLUS, lexeme="+", literal=None, line=3
                        ),
                        right=Literal(value="hello"),
                    ),
                    operator=Token(
                        token_type=TokenType.PLUS, lexeme="+", literal=None, line=3
                    ),
                    right=Literal(value="quz"),
                )
            ),
        ]

    def test_parses_variable_declarations(self):
        source = 'var foo = "bar";'
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Var(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=1
                ),
                initializer=Literal(value="bar"),
            )
        ]

    def test_parses_assignments(self):
        source = 'foo = "bar";'
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Expression(
                expression=Assign(
                    name=Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="foo",
                        literal=None,
                        line=1,
                    ),
                    value=Literal(value="bar"),
                )
            )
        ]

    def test_parses_blocks(self):
        source = """
        {
            var foo = "bar";
        }
        {
            var foo = "baz";
        }
        """
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Block(
                statements=[
                    Var(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="foo",
                            literal=None,
                            line=3,
                        ),
                        initializer=Literal(value="bar"),
                    )
                ]
            ),
            Block(
                statements=[
                    Var(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="foo",
                            literal=None,
                            line=6,
                        ),
                        initializer=Literal(value="baz"),
                    )
                ]
            ),
        ]

    def test_parses_if_statements(self):
        source = """
        var foo;
        if (17 < 42) {
            foo = "bar";
        } else {
            foo = "baz";
        }
        print foo;
        """
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        print(stmts)
        assert stmts == [
            Var(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=2
                ),
                initializer=None,
            ),
            If(
                condition=Binary(
                    left=Literal(value=17.0),
                    operator=Token(
                        token_type=TokenType.LESS, lexeme="<", literal=None, line=3
                    ),
                    right=Literal(value=42.0),
                ),
                then_branch=Block(
                    statements=[
                        Expression(
                            expression=Assign(
                                name=Token(
                                    token_type=TokenType.IDENTIFIER,
                                    lexeme="foo",
                                    literal=None,
                                    line=4,
                                ),
                                value=Literal(value="bar"),
                            )
                        )
                    ]
                ),
                else_branch=Block(
                    statements=[
                        Expression(
                            expression=Assign(
                                name=Token(
                                    token_type=TokenType.IDENTIFIER,
                                    lexeme="foo",
                                    literal=None,
                                    line=6,
                                ),
                                value=Literal(value="baz"),
                            )
                        )
                    ]
                ),
            ),
            Print(
                expression=Variable(
                    name=Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="foo",
                        literal=None,
                        line=8,
                    )
                )
            ),
        ]
