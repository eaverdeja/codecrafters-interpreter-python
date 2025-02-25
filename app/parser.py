from dataclasses import dataclass
from typing import Callable

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
from app.stmt import Block, Expression, Function, If, Print, Stmt, Var, While


class ParseError(RuntimeError): ...


@dataclass
class Parser:
    """
    Grammar

    program        → declaration* EOF ;
    declaration    → varDecl
                    | funDecl
                    | statement ;
    statement      → exprStmt
                    | ifStmt
                    | printStmt
                    | whileStmt
                    | forStmt
                    | block ;
    exprStmt       → expression ";" ;
    ifStmt         → "if" "(" expression ")" statetment ( "else" statement )? ;
    printStmt      → "print" expression ";" ;
    whileStmt      → "while" "(" expression ")" statement ;
    forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                     expression? ";"
                     expression? ")" statement ;
    block          → "{" declaration* "}" ;

    expression     → assignment ;
    assignment     → IDENTIFIER "=" assignment
                    | equality
                    | logic_or ;
    logic_or       → logic_and ( "or" logic_and )* ;
    logic_and      → equality ( "and" equality )* ;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           → factor ( ( "-" | "+" ) factor )* ;
    factor         → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary | call ;
    call           → primary ( "(" arguments? ")" )* ;
    arguments      → expression ( "," expression )* ;
    primary        → "true" | "false" | "nil"
                    | NUMBER | STRING
                    | "(" expression ")"
                    | IDENTIFIER ;
    varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
    funDecl        → "fun" function ;
    function       → IDENTIFIER "(" parameters? ")" block ;
    parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
    """

    tokens: list[Token]
    error_reporter: Callable[[Token, str], None]

    _current: int = 0

    def parse(self) -> Expr | None:
        try:
            return self._expression()
        except ParseError:
            return None

    def parse_all(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._is_at_end():
            declaration = self._declaration()
            if declaration:
                statements.append(declaration)
        return statements

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error_reporter(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._call()

    def _call(self) -> Expr:
        expr = self._primary()

        while self._match(TokenType.LEFT_PAREN):
            expr = self._finish_call(expr)

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) > 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal("false")
        if self._match(TokenType.TRUE):
            return Literal("true")
        if self._match(TokenType.NIL):
            return Literal("nil")
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)
        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()

            return self._statement()
        except ParseError as e:
            self._synchronize()
            return None

    def _statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.LEFT_BRACE):
            return Block(self._block())
        return self._expression_statement()

    def _print_statement(self) -> Stmt:
        val = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(val)

    def _if_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _while_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")

        body = self._statement()

        return While(condition, body)

    def _for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Stmt | None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition: Expr
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Expr | None = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "expect ')' after for clauses.")

        body = self._statement()

        if increment:
            body = Block([body, Expression(increment)])

        if not condition:
            condition = Literal("true")
        body = While(condition, body)

        if initializer:
            body = Block([initializer, body])

        return body

    def _block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after a block.")
        return statements

    def _expression_statement(self) -> Stmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def _function(self, kind: str) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) > 255:
                    self._error(self._peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self._consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before" + f" {kind} body.")
        body = self._block()

        return Function(name, parameters, body)

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Expr | None = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: Token, message: str) -> ParseError:
        self.error_reporter(token, message)
        return ParseError(message)

    def _synchronize(self):
        self._advance()
        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return
            match self._peek().token_type:
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.FOR
                    | TokenType.IF
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return
            self._advance()

    def _is_at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self._current]

    def _previous(self) -> Token:
        return self.tokens[self._current - 1]
