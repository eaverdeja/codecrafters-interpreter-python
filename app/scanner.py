from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable


class TokenType(StrEnum):
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
    EOF = "EOF"


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: None
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
            case default:
                self.error_reporter(self._line, f"Unexpected character: {default}")

    def _advance(self) -> str:
        char = self.source[self._current]
        self._current += 1
        return char

    def _add_token(self, token: TokenType, literal: None = None) -> None:
        text = self.source[self._start : self._current]
        self._tokens.append(Token(token, text, literal, self._line))
