import sys

from app.ast_printer import AstPrinter
from app.expr import Expr
from app.interpreter import Interpreter
from app.parser import Parser
from app.scanner import Scanner, Token, TokenType


class Pylox:
    _had_error = False

    def main(self) -> None:
        if len(sys.argv) == 1:
            self.run_prompt()
            exit(0)

        if len(sys.argv) == 2:
            filename = sys.argv[1]
            self.run_file(filename)
            exit(0)

        command = sys.argv[1]
        filename = sys.argv[2]

        match command:
            case "tokenize":
                tokens = self.scan_file(filename)
                for token in tokens:
                    print(token)
            case "parse":
                expr = self.parse_file(filename)
                if expr:
                    ast = AstPrinter().print(expr)
                    print(ast)
            case "evaluate":
                expr = self.parse_file(filename)
                if expr:
                    res = Interpreter().interpret(expr)
                    print(res)
            case _:
                print(f"Unknown command: {command}", file=sys.stderr)
                exit(1)

        if self._had_error:
            exit(65)

    def run_file(self, filename: str) -> None:
        with open(filename) as file:
            file_contents = file.read()

        self.run(file_contents)

        if self._had_error:
            exit(65)

    def run_prompt(self) -> None:
        while True:
            sys.stdout.write("> ")
            sys.stdout.flush()
            try:
                line = input()
            except EOFError:
                break
            if not line:
                continue

            self.run(line)
            self._had_error = False

    def run(self, source: str) -> None:
        tokens = self._scan(source)
        expr = self._parse(tokens)

        if self._had_error:
            return
        assert (
            expr is not None
        ), "Expected valid expression since no errors were reported!"

        res = Interpreter().interpret(expr)
        print(res)

    def scan_file(self, filename: str) -> list[Token]:
        with open(filename) as file:
            source = file.read()
        return self._scan(source)

    def parse_file(self, filename: str) -> Expr | None:
        tokens = self.scan_file(filename)
        return self._parse(tokens)

    def _scan(self, source: str) -> list[Token]:
        scanner = Scanner(source, error_reporter=self.scan_error)
        return scanner.scan_tokens()

    def _parse(self, tokens: list[Token]) -> Expr | None:
        return Parser(tokens, error_reporter=self.parse_error).parse()

    def scan_error(self, line: int, message: str) -> None:
        self._report(line, "", message)

    def parse_error(self, token: Token, message: str) -> None:
        if token.token_type == TokenType.EOF:
            self._report(token.line, " at the end", message)
        else:
            self._report(token.line, f" at '{token.lexeme}'", message)

    def _report(self, line: int, where: str, message: str):
        sys.stderr.write(f"[line {line}] Error{where}: {message}\n")
        self._had_error = True


if __name__ == "__main__":
    Pylox().main()
