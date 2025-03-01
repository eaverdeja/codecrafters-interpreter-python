import time
from unittest.mock import MagicMock, call

from pytest import CaptureFixture
from app.expr import Expr
from app.interpreter import Interpreter, RuntimeException
from app.parser import Parser
from app.resolver import Resolver
from app.scanner import Scanner, Token, TokenType
from app.stmt import Stmt


class TestInterpret:
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


class TestInterpretAll:
    def generate_statements(self, source: str) -> list[Stmt]:
        tokens = Scanner(source=source, error_reporter=MagicMock()).scan_tokens()
        stmts = Parser(tokens, error_reporter=MagicMock()).parse_all()
        return stmts

    def test_can_execute_a_print_statement(self, capsys: CaptureFixture):
        stmts = self.generate_statements('print "hello" + ", world!";')

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "hello, world!\n"

    def test_can_execute_expression_statements(self, capsys):
        source = """
        print 42 > 17;
        print "the expression below is invalid";
        14 + "quz";
        print "this should not be printed";
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "true\nthe expression below is invalid\n"

    def test_can_execute_variable_declarations(self, capsys):
        source = """
        var a = 1;
        var b = 2;
        print a + b;
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "3\n"

    def test_can_execute_variable_assignments(self, capsys):
        source = """
        var foo = 1;
        var bar = 3;
        foo = bar = 2;
        print foo;
        print bar;
        print foo = 3;
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "2\n2\n3\n"

    def test_can_execute_multiple_blocks(self, capsys):
        source = """
        var a = "global a";
        var b = "global b";
        var c = "global c";
        {
            var a = "outer a";
            var b = "outer b";
            {
                var a = "inner a";
                print a;
                print b;
                print c;
            }
            print a;
            print b;
            print c;
        }
        print a;
        print b;
        print c;
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert (
            captured.out
            == """inner a
outer b
global c
outer a
outer b
global c
global a
global b
global c
"""
        )

    def test_can_execute_if_statemens(self, capsys):
        source = """
        var foo;
        if (17 < 42) {
            foo = "bar";
        } else {
            foo = "baz";
        }
        print foo;
        """

        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "bar\n"

    def test_can_execute_logical_expressions(self, capsys):
        source = "print true or false and true;"
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "true\n"

    def test_can_execute_while_statements(self, capsys):
        source = """
        var i = 0;
        while (i < 2) {
            i = i + 1;
            print i;
        }
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "1\n2\n"

    def test_can_execute_native_functions(self, capsys):
        source = "print clock();"
        stmts = self.generate_statements(source)

        start_time = time.time()
        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)
        end_time = time.time()

        captured = capsys.readouterr()
        captured_time = float(captured.out.strip("\n"))
        assert start_time < captured_time < end_time

    def test_can_execute_functions_with_no_arguments(self, capsys):
        source = """
        fun bar() { print 10; }
        bar();
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "10\n"

    def test_can_execute_functions_with_arguments(self, capsys):
        source = """
        fun bar(a, b) { print a + b; }
        bar(1, 2);
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "3\n"

    def test_can_execute_functions_with_return_statements(self, capsys):
        source = """
        fun bar(a, b) { return a * b; }
        print(bar(2, 2));
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "4\n"

    def test_can_execute_higher_order_functions(self, capsys):
        source = """
        fun makeFilter(min) {
            fun filter(n) {
                if (n < min) {
                    return false;
                }
                return true;
            }
            return filter;
        }

        var greaterThan55 = makeFilter(55);
        print(greaterThan55(60));
        """
        stmts = self.generate_statements(source)

        Interpreter(error_reporter=MagicMock()).interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "true\n"

    def test_can_properly_bind_variables_when_coupled_with_a_resolver(self, capsys):
        source = """
        var a = "global";
        {
            fun showA() {
                print a;
            }

            showA();
            var a = "block";
            showA();
        }
        """
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())
        Resolver(interpreter, error_reporter=MagicMock()).resolve(stmts)

        interpreter.interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "global\nglobal\n"

    def test_can_properly_detect_illegal_top_level_return_statements(self):
        source = 'return "at the top-level";'
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())

        error_reporter = MagicMock()
        Resolver(interpreter, error_reporter=error_reporter).resolve(stmts)

        error_reporter.assert_called_once_with(
            Token(token_type=TokenType.RETURN, lexeme="return", literal=None, line=1),
            "Can't return from top-level code.",
        )

    def test_can_properly_detect_unused_variables(self):
        source = """
        {
            var a = "foo";
            {
                var b = "bar";
            }
            {
                var c = "bazzz";
                print c;
            }
            print "foo!";
        }
        """
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())

        error_reporter = MagicMock()
        Resolver(interpreter, error_reporter=error_reporter).resolve(stmts)

        assert len(error_reporter.call_args_list) == 2
        error_reporter.assert_has_calls(
            [
                call(
                    Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="a",
                        literal=None,
                        line=3,
                    ),
                    "Unused variable.",
                ),
                call(
                    Token(
                        token_type=TokenType.IDENTIFIER,
                        lexeme="b",
                        literal=None,
                        line=5,
                    ),
                    "Unused variable.",
                ),
            ]
        )

    def test_can_interpret_class_declarations(self, capsys):
        source = """
        class DevonshireCream {
            serveOn() {
                return "Scones";
            }
        }

        print DevonshireCream;
        """
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())
        Resolver(interpreter, error_reporter=MagicMock()).resolve(stmts)

        interpreter.interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "DevonshireCream\n"

    def test_can_execute_get_and_set_expressions(self, capsys):
        source = """
        class Bagel {}
        var bagel = Bagel();
        bagel.size = "large";
        print bagel.size;
        """
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())
        Resolver(interpreter, error_reporter=MagicMock()).resolve(stmts)

        interpreter.interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "large\n"

    def test_can_execute_methods_on_instances(self, capsys):
        source = """
        class Spaceship {
            fly() {
                print "vrummm";
            }
        }
        var spaceship = Spaceship();
        spaceship.fly();
        """
        stmts = self.generate_statements(source)
        interpreter = Interpreter(error_reporter=MagicMock())
        Resolver(interpreter, error_reporter=MagicMock()).resolve(stmts)

        interpreter.interpret_all(stmts)

        captured = capsys.readouterr()
        assert captured.out == "vrummm\n"
