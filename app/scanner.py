from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable


class TokenType(StrEnum):
    # Single character tokens
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    STAR = "STAR"
    SLASH = "SLASH"

    # One or two character tokens
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"

    # Literals
    STRING = "STRING"
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"

    EOF = "EOF"


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: object
    line: int

    def __str__(self) -> str:
        literal = self.literal or "null"
        return f"{self.token_type} {self.lexeme} {literal}"


@dataclass
class Scanner:
    source: str
    error_reporter: Callable[..., None]

    _start: int = 0
    _current: int = 0
    _line: int = 1
    _tokens: list[Token] = field(default_factory=list)

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens

    def _is_at_end(self) -> bool:
        return self._current >= len(self.source)

    def _scan_token(self) -> None:
        c = self._advance()
        match c:
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "!":
                self._add_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                self._add_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case ">":
                self._add_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "<":
                self._add_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case "/":
                if self._match("/"):
                    # A comment goes until the end of the line
                    while self._peek() != "\n":
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)
            case '"':
                self._string()
            case " " | "\r" | "\t":
                # Ignore whitespace
                pass
            case "\n":
                self._line += 1
            case default:
                if self._is_digit(c):
                    self._number()
                    return
                if self._is_alpha(c):
                    self._identifier()
                    return

                self.error_reporter(self._line, f"Unexpected character: {default}")

    def _advance(self) -> str:
        char = self.source[self._current]
        self._current += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\n"
        return self.source[self._current]

    def _peek_next(self) -> str:
        if self._current + 1 >= len(self.source):
            return "\n"
        return self.source[self._current + 1]

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()
        if self._is_at_end():
            self.error_reporter(self._line, "Unterminated string.")
            return

        # The closing "
        self._advance()

        value = self.source[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, value)

    def _number(self) -> None:
        while self._is_digit(self._peek()):
            self._advance()

        # Look for fractional part
        if self._peek() == "." and self._is_digit(self._peek_next()):
            # Consume the "."
            self._advance()

            while self._is_digit(self._peek()):
                self._advance()

        value = float(self.source[self._start : self._current])
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self) -> None:
        while self._is_alphanumeric(self._peek()):
            self._advance()

        self._add_token(TokenType.IDENTIFIER)

    def _is_digit(self, char: str) -> bool:
        return "0" <= char <= "9"

    def _is_alpha(self, char: str) -> bool:
        return (
            (char >= "a" and char <= "z")
            or (char >= "A" and char <= "Z")
            or char == "_"
        )

    def _is_alphanumeric(self, char) -> bool:
        return self._is_digit(char) or self._is_alpha(char)

    def _add_token(self, token: TokenType, literal: object | None = None) -> None:
        text = self.source[self._start : self._current]
        self._tokens.append(Token(token, text, literal, self._line))
