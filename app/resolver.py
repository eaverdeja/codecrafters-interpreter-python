from dataclasses import dataclass, field
from collections import deque
from typing import Callable, Deque
from enum import StrEnum, auto

from app import expr, stmt
from app.interpreter import Interpreter
from app.scanner import Token, TokenType


class FunctionType(StrEnum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(StrEnum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class VariableState(StrEnum):
    DECLARED = auto()
    DEFINED = auto()
    IN_USE = auto()


@dataclass
class Resolver(expr.Visitor, stmt.Visitor):
    interpreter: Interpreter
    error_reporter: Callable[[Token, str], None]

    scopes: Deque[dict[Token, VariableState]] = field(default_factory=deque)
    _current_function: FunctionType = field(default=FunctionType.NONE)
    _current_class: ClassType = field(default=ClassType.NONE)
    _unused_vars: list[Token] = field(default_factory=list)

    def resolve(self, statements: list[stmt.Stmt]) -> None:
        self._resolve(statements)
        self._report_unused_variables()

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer:
            self._resolve_expr(stmt.initializer)
        self._define(stmt.name)

    def visit_variable_expr(self, expr: expr.Variable) -> None:
        if (
            len(self.scopes) > 0
            and self.scopes[-1].get(expr.name) == VariableState.DECLARED
        ):
            self.error_reporter(
                expr.name, "Can't read local variable in its own initializer."
            )

        self._resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: expr.Assign) -> None:
        self._resolve_expr(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_set_expr(self, expr: expr.Set) -> None:
        self._resolve_expr(expr.value)
        self._resolve_expr(expr.object)

    def visit_this_expr(self, expr: expr.This) -> None:
        if self._current_class == ClassType.NONE:
            self.error_reporter(expr.keyword, "Can't use 'this' outside of a class.")
            return

        self._resolve_local(expr, expr.keyword)

    def visit_super_expr(self, expr: expr.Super) -> None:
        if self._current_class == ClassType.NONE:
            self.error_reporter(expr.keyword, "Can't use 'super' outside of a class.")
        elif self._current_class == ClassType.CLASS:
            self.error_reporter(
                expr.keyword, "Can't use 'super' in a class with no superclass."
            )
        self._resolve_local(expr, expr.keyword)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_class_stmt(self, stmt: stmt.Class) -> None:
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS

        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass and stmt.superclass.name.lexeme == stmt.name.lexeme:
            self.error_reporter(stmt.name, "A class can't inherit from itself.")

        if stmt.superclass:
            self._current_class = ClassType.SUBCLASS
            self._resolve_expr(stmt.superclass)
            self._begin_scope()
            _super = Token(TokenType.SUPER, "super", None, stmt.name.line)
            self.scopes[-1][_super] = VariableState.IN_USE

        self._begin_scope()

        this = Token(TokenType.THIS, "this", None, stmt.name.line)
        self.scopes[-1][this] = VariableState.IN_USE
        for method in stmt.methods:
            fun_type = (
                FunctionType.METHOD
                if method.name.lexeme != "init"
                else FunctionType.INITIALIZER
            )
            self._resolve_function(method, fun_type)

        self._end_scope()

        if stmt.superclass:
            self._end_scope()

        self._current_class = enclosing_class

    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self._resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt: stmt.If) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.then_branch)
        if stmt.else_branch:
            self._resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        self._resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: stmt.Return) -> None:
        if len(self.scopes) == 0:
            self.error_reporter(stmt.keyword, "Can't return from top-level code.")
            return
        if stmt.value:
            if self._current_function == FunctionType.INITIALIZER:
                self.error_reporter(
                    stmt.keyword, "Can't return a value from an initializer."
                )
                return
            self._resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt: stmt.While) -> None:
        self._resolve_expr(stmt.condition)
        self._resolve_stmt(stmt.body)

    def visit_binary_expr(self, expr: expr.Binary) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_call_expr(self, expr: expr.Call) -> None:
        self._resolve_expr(expr.callee)
        for arg in expr.arguments:
            self._resolve_expr(arg)

    def visit_get_expr(self, expr: expr.Get) -> None:
        self._resolve_expr(expr.object)

    def visit_grouping_expr(self, expr: expr.Grouping) -> None:
        self._resolve_expr(expr.expression)

    def visit_literal_expr(self, _: expr.Literal) -> None: ...

    def visit_logical_expr(self, expr: expr.Logical) -> None:
        self._resolve_expr(expr.left)
        self._resolve_expr(expr.right)

    def visit_unary_expr(self, expr: expr.Unary) -> None:
        self._resolve_expr(expr.right)

    def _begin_scope(self) -> None:
        self.scopes.append({})

    def _end_scope(self) -> None:
        scope = self.scopes.pop()
        for var, state in scope.items():
            if not state == VariableState.IN_USE:
                self._unused_vars.append(var)

    def _resolve(self, statements: list[stmt.Stmt]) -> None:
        for statement in statements:
            self._resolve_stmt(statement)

    def _resolve_stmt(self, statement: stmt.Stmt) -> None:
        statement.accept(self)

    def _resolve_expr(self, expr: expr.Expr) -> None:
        expr.accept(self)

    def _resolve_function(
        self, stmt: stmt.Function, function_type: FunctionType
    ) -> None:
        enclosing_function = self._current_function
        self._current_function = function_type
        self._begin_scope()

        for param in stmt.params:
            self._declare(param)
            self._define(param)
        self._resolve(stmt.body)

        self._end_scope()
        self._current_function = enclosing_function

    def _declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name] = VariableState.DECLARED

    def _define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name] = VariableState.DEFINED

    def _resolve_local(self, expr: expr.Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            for token in self.scopes[i]:
                if name.lexeme == token.lexeme:
                    self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                    self.scopes[i][token] = VariableState.IN_USE
                    return

    def _report_unused_variables(self) -> None:
        for var in reversed(self._unused_vars):
            self.error_reporter(var, "Unused variable.")
