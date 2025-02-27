from typing import Callable, TypeGuard, cast
from dataclasses import dataclass, field
import time

from app import expr, stmt
from app.environment import Environment
from app.exceptions import RuntimeException
from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction
from app.returner import Return
from app.stmt import (
    Block,
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
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from app.scanner import Token, TokenType


@dataclass
class Interpreter(expr.Visitor[object], stmt.Visitor[None]):
    error_reporter: Callable[..., None]

    _globals: Environment = field(default_factory=Environment)
    _locals: dict[Expr, int] = field(default_factory=dict)
    _environment: Environment = field(init=False)

    def __post_init__(self):
        class Clock(LoxCallable):
            def arity(self):
                return 0

            def call(
                self, _interpreter: Interpreter, _arguments: list[object]
            ) -> object:
                return time.time()

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
        self._locals[expr] = depth

    def visit_literal_expr(self, expr: Literal) -> object:
        if isinstance(expr.value, float) and expr.value.is_integer():
            return int(expr.value)
        if expr.value == "true":
            return True
        if expr.value == "false":
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

    def visit_unary_expr(self, expr: Unary) -> object:
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                val = not self._is_truthy(right)
                return val
            case TokenType.MINUS:
                if self._check_number_operand(right, expr.operator):
                    return -right
        return None

    def visit_binary_expr(self, expr: Binary) -> object:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise RuntimeException(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right

        if self._check_number_operand(
            left, expr.operator
        ) and self._check_number_operand(right, expr.operator):
            match expr.operator.token_type:
                case TokenType.MINUS:
                    return left - right
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
        function = LoxFunction(stmt, self._environment)
        self._environment.define(stmt.name.lexeme, function)

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

        distance = self._locals.get(expr)
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

    def _lookup_variable(self, name: Token, expr: Variable) -> object:
        if not self._locals:
            return self._environment.get(expr.name)

        distance = self._locals.get(expr)
        if distance is None:
            return self._globals.get(name)
        return self._environment.get_at(distance, name)

    def _is_truthy(self, obj: object) -> bool:
        if obj is None or obj == False or obj == "nil":
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
