from typing import Callable, TypeGuard, cast
from dataclasses import dataclass, field
import time

from app import expr, stmt
from app.environment import Environment
from app.exceptions import RuntimeException
from app.lox_callable import LoxCallable
from app.lox_class import LoxClass
from app.lox_function import LoxFunction
from app.lox_instance import LoxInstance
from app.returner import Return
from app.stmt import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return as ReturnStmt,
    Stmt,
    Var,
    While,
)
from app.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from app.scanner import Token, TokenType
from app.variable_ref import VariableRef


@dataclass
class Interpreter(expr.Visitor[object], stmt.Visitor[None]):
    error_reporter: Callable[..., None]

    _globals: Environment = field(default_factory=Environment)
    _locals: dict[VariableRef, int] = field(default_factory=dict)
    _environment: Environment = field(init=False)

    def __post_init__(self):
        class Clock(LoxCallable):
            def arity(self):
                return 0

            def call(
                self, _interpreter: Interpreter, _arguments: list[object]
            ) -> object:
                return time.time()

            def __str__(self):
                return "<native fn>"

        self._globals.define("clock", Clock())
        self._environment = self._globals

    def interpret(self, expr: Expr) -> str | None:
        try:
            val = self._evaluate(expr)
            return self._stringify(val)
        except RuntimeException as e:
            self.error_reporter(e)
            return None

    def interpret_all(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeException as e:
            self.error_reporter(e)

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[VariableRef(expr)] = depth

    def visit_literal_expr(self, expr: Literal) -> object:
        if isinstance(expr.value, float) and expr.value.is_integer():
            return int(expr.value)
        if expr.value is True:
            return True
        if expr.value is False:
            return False
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> object:
        left = self._evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self._evaluate(expr.expression)

    def visit_call_expr(self, expr: Call) -> object:
        callee = self._evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeException(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeException(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_get_expr(self, expr: Get) -> object:
        obj = self._evaluate(expr.object)
        if not isinstance(obj, LoxInstance):
            raise RuntimeException(expr.name, "Only instances have properties.")

        return obj.get(expr.name)

    def visit_set_expr(self, expr: Set) -> object:
        obj = self._evaluate(expr.object)
        if not isinstance(obj, LoxInstance):
            raise RuntimeException(expr.name, "Only instances have fields.")

        value = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_this_expr(self, expr: This) -> object:
        return self._lookup_variable(expr.keyword, expr)

    def visit_super_expr(self, expr: Super) -> object:
        distance = self._locals[VariableRef(expr)]
        superclass = cast(LoxClass, self._environment.get_at(distance, "super"))
        # Offsetting the distance by one looks up “this” in the inner environment of "super"
        obj = self._environment.get_at(distance - 1, "this")

        method = superclass.find_method(expr.method.lexeme)
        if not method:
            raise RuntimeException(
                expr.method, f"Undefined property '{expr.method.lexeme}'."
            )
        if not isinstance(obj, LoxInstance):
            raise RuntimeException(
                expr.method, "Could not retrieve instace of subclass."
            )

        return method.bind(obj)

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                val = not self._is_truthy(right)
                return val
            case TokenType.MINUS:
                if self._check_number_operand(right, expr.operator):
                    # Python can't reproduce -0 by default,
                    # and math.copysign returns floats.
                    # So we gotta hack it, unfortunately
                    if right == 0:
                        return str("-0")
                    return -right
        return None

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        # Handle the -0 hack
        if left == "-0":
            left = 0
        if right == "-0":
            right = 0

        match expr.operator.token_type:
            case TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if not isinstance(left, bool) and not isinstance(right, bool):
                        return left + right
                if isinstance(left, str) and isinstance(right, str):
                    reserved = ("true", "false", "nil")
                    if left not in reserved and right not in reserved:
                        return left + right
                raise RuntimeException(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.BANG_EQUAL:
                if isinstance(left, bool) or isinstance(right, bool):
                    return left is not right
                return left != right
            case TokenType.EQUAL_EQUAL:
                if (
                    isinstance(left, LoxCallable)
                    or isinstance(right, LoxCallable)
                    or isinstance(left, bool)
                    or isinstance(right, bool)
                ):
                    return left is right
                return left == right

        if self._check_number_operands(left, right, expr.operator):
            left = cast(float, left)
            right = cast(float, right)

            match expr.operator.token_type:
                case TokenType.MINUS:
                    val = left - right
                    if isinstance(val, float) and val.is_integer():
                        return int(val)
                    return val
                case TokenType.STAR:
                    return left * right
                case TokenType.SLASH:
                    val = left / right
                    if val.is_integer():
                        return int(val)
                    return val
                case TokenType.GREATER:
                    return left > right
                case TokenType.GREATER_EQUAL:
                    return left >= right
                case TokenType.LESS:
                    return left < right
                case TokenType.LESS_EQUAL:
                    return left <= right

        return None

    def visit_print_stmt(self, stmt: Print) -> None:
        val = self._evaluate(stmt.expression)
        print(self._stringify(val))

    def visit_if_stmt(self, stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt.statements, Environment(enclosing=self._environment))

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_var_stmt(self, stmt: Var) -> None:
        val: object | None = None
        if stmt.initializer:
            val = self._evaluate(stmt.initializer)
        self._environment.define(stmt.name.lexeme, val)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)

    def visit_class_stmt(self, stmt: Class):
        environment = self._environment
        environment.define(stmt.name.lexeme, None)

        superclass = None
        if stmt.superclass:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeException(
                    stmt.superclass.name, "Superclass must be a class."
                )
            environment = Environment(enclosing=environment)
            environment.define("super", superclass)

        methods = {
            method.name.lexeme: LoxFunction(
                method,
                environment,
                is_initializer=method.name.lexeme == "init",
            )
            for method in stmt.methods
        }
        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass:
            environment = environment.enclosing

        environment.assign(stmt.name, klass)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        value: object = None
        if stmt.value:
            value = self._evaluate(stmt.value)

        raise Return(value)

    def visit_variable_expr(self, expr: Variable) -> object:
        return self._lookup_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign) -> object:
        val = self._evaluate(expr.value)
        if not self._locals:
            self._environment.assign(expr.name, val)
            return val

        distance = self._locals.get(VariableRef(expr))
        if distance is not None:
            self._environment.assign_at(distance, expr.name, val)
        else:
            self._globals.assign(expr.name, val)
        return val

    def _evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def _execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self._environment
        try:
            self._environment = environment
            for stmt in statements:
                self._execute(stmt)
        finally:
            self._environment = previous

    def _lookup_variable(self, name: Token, expr: Variable | This) -> object:
        if not self._locals:
            return self._environment.get(expr.name)

        distance = self._locals.get(VariableRef(expr))
        if distance is None:
            return self._globals.get(name)
        return self._environment.get_at(distance, name.lexeme)

    def _is_truthy(self, obj: object) -> bool:
        if obj is None or obj is False or obj == "nil":
            return False
        return True

    def _stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"
        if obj is True or obj is False:
            return str(obj).lower()
        return str(obj)

    def _check_number_operand(
        self, operand: object, operator: Token
    ) -> TypeGuard[int | float]:
        # isinstance(True, int) evaluates to True in python :/
        if not isinstance(operand, bool) and isinstance(operand, (int, float)):
            return True
        raise RuntimeException(operator, "Operand must be a number.")

    def _check_number_operands(
        self, left: object, right: object, operator: Token
    ) -> TypeGuard[int | float]:
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        raise RuntimeException(operator, "Operands must be numbers.")
