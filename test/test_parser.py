from unittest import mock
from unittest.mock import MagicMock
from app.expr import (
    Assign,
    Binary,
    Call,
    Get,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType
from app.stmt import Block, Class, Expression, Function, If, Print, Return, Var, While


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

    def test_parses_logical_operators(self):
        source = "true and false or true;"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Expression(
                expression=Logical(
                    left=Logical(
                        left=Literal(value="true"),
                        operator=Token(
                            token_type=TokenType.AND, lexeme="and", literal=None, line=1
                        ),
                        right=Literal(value="false"),
                    ),
                    operator=Token(
                        token_type=TokenType.OR, lexeme="or", literal=None, line=1
                    ),
                    right=Literal(value="true"),
                )
            )
        ]

    def test_parses_while_statements(self):
        source = """
        while (true) {
            print "forever and ever";
        }
        """
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            While(
                condition=Literal(value="true"),
                body=Block(
                    statements=[Print(expression=Literal(value="forever and ever"))]
                ),
            )
        ]

    def test_parses_for_statements(self):
        source = "for (var baz = 0; baz < 3;) print baz = baz + 1;"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Block(
                statements=[
                    Var(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="baz",
                            literal=None,
                            line=1,
                        ),
                        initializer=Literal(value=0.0),
                    ),
                    While(
                        condition=Binary(
                            left=Variable(
                                name=Token(
                                    token_type=TokenType.IDENTIFIER,
                                    lexeme="baz",
                                    literal=None,
                                    line=1,
                                )
                            ),
                            operator=Token(
                                token_type=TokenType.LESS,
                                lexeme="<",
                                literal=None,
                                line=1,
                            ),
                            right=Literal(value=3.0),
                        ),
                        body=Print(
                            expression=Assign(
                                name=Token(
                                    token_type=TokenType.IDENTIFIER,
                                    lexeme="baz",
                                    literal=None,
                                    line=1,
                                ),
                                value=Binary(
                                    left=Variable(
                                        name=Token(
                                            token_type=TokenType.IDENTIFIER,
                                            lexeme="baz",
                                            literal=None,
                                            line=1,
                                        )
                                    ),
                                    operator=Token(
                                        token_type=TokenType.PLUS,
                                        lexeme="+",
                                        literal=None,
                                        line=1,
                                    ),
                                    right=Literal(value=1.0),
                                ),
                            )
                        ),
                    ),
                ]
            )
        ]

    def test_parses_function_calls_without_arguments(self):
        source = "foo();"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Expression(
                expression=Call(
                    callee=Variable(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="foo",
                            literal=None,
                            line=1,
                        )
                    ),
                    paren=Token(
                        token_type=TokenType.RIGHT_PAREN,
                        lexeme=")",
                        literal=None,
                        line=1,
                    ),
                    arguments=[],
                )
            )
        ]

    def test_parses_function_calls_with_arguments(self):
        source = "foo(1, 2);"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Expression(
                expression=Call(
                    callee=Variable(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="foo",
                            literal=None,
                            line=1,
                        )
                    ),
                    paren=Token(
                        token_type=TokenType.RIGHT_PAREN,
                        lexeme=")",
                        literal=None,
                        line=1,
                    ),
                    arguments=[Literal(value=1.0), Literal(value=2.0)],
                )
            )
        ]

    def test_parses_function_declarations_without_arguments(self):
        source = 'fun foo() { print "foo!"; }'
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Function(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=1
                ),
                params=[],
                body=[Print(expression=Literal(value="foo!"))],
            )
        ]

    def test_parses_function_declarations_with_arguments(self):
        source = "fun foo(a) { print a; }"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Function(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=1
                ),
                params=[
                    Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="a",
                        literal=None,
                        line=1,
                    )
                ],
                body=[
                    Print(
                        expression=Variable(
                            name=Token(
                                token_type=TokenType.IDENTIFIER,
                                lexeme="a",
                                literal=None,
                                line=1,
                            )
                        )
                    )
                ],
            )
        ]

    def test_parses_return_statements(self):
        source = "fun foo(a) { return a; }"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Function(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="foo", literal=None, line=1
                ),
                params=[
                    Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="a",
                        literal=None,
                        line=1,
                    )
                ],
                body=[
                    Return(
                        keyword=Token(
                            token_type=TokenType.RETURN,
                            lexeme="return",
                            literal=None,
                            line=1,
                        ),
                        value=Variable(
                            name=Token(
                                token_type=TokenType.IDENTIFIER,
                                lexeme="a",
                                literal=None,
                                line=1,
                            )
                        ),
                    )
                ],
            )
        ]

    def test_parses_classes(self):
        source = """
        class Foo {
            foo() {
                print "foo!";
            }
            
            bar() {
                print "bar!";
            }
        }
        """
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Class(
                name=Token(
                    token_type=TokenType.IDENTIFIER, lexeme="Foo", literal=None, line=2
                ),
                methods=[
                    Function(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="foo",
                            literal=None,
                            line=3,
                        ),
                        params=[],
                        body=[Print(expression=Literal(value="foo!"))],
                    ),
                    Function(
                        name=Token(
                            token_type=TokenType.IDENTIFIER,
                            lexeme="bar",
                            literal=None,
                            line=7,
                        ),
                        params=[],
                        body=[Print(expression=Literal(value="bar!"))],
                    ),
                ],
            )
        ]

    def test_parses_get_expressions(self):
        source = "foo.bar().baz;"
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()

        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()

        assert stmts == [
            Expression(
                expression=Get(
                    object=Call(
                        callee=Get(
                            object=Variable(
                                name=Token(
                                    token_type=TokenType.IDENTIFIER,
                                    lexeme="foo",
                                    literal=None,
                                    line=1,
                                )
                            ),
                            name=Token(
                                token_type=TokenType.IDENTIFIER,
                                lexeme="bar",
                                literal=None,
                                line=1,
                            ),
                        ),
                        paren=Token(
                            token_type=TokenType.RIGHT_PAREN,
                            lexeme=")",
                            literal=None,
                            line=1,
                        ),
                        arguments=[],
                    ),
                    name=Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="baz",
                        literal=None,
                        line=1,
                    ),
                )
            )
        ]
