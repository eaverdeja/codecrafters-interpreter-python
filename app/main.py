import sys

from app.ast_printer import AstPrinter
from app.expr import Expr
from app.interpreter import Interpreter, RuntimeException
from app.parser import Parser
from app.resolver import Resolver
from app.scanner import Scanner, Token, TokenType
from app.stmt import Expression, Stmt


class Pylox:
    _had_error = False
    _had_runtime_error = False
    _interpreter: Interpreter

    def __init__(self) -> None:
        self._interpreter = Interpreter(error_reporter=self.runtime_error)

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
                    res = self._interpreter.interpret(expr)
                    if res:
                        print(res)
            case "run":
                self.run_file(filename)
            case _:
                print(f"Unknown command: {command}", file=sys.stderr)
                exit(1)

        self._handle_errors()

    def run_file(self, filename: str) -> None:
        with open(filename) as file:
            file_contents = file.read()

        self.run(file_contents)
        self._handle_errors()

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
        stmts = self._parse_all(tokens)

        if self._had_error:
            return

        resolver = Resolver(self._interpreter, error_reporter=self.resolution_error)
        resolver.resolve(stmts)

        if self._had_error:
            return

        self._interpreter.interpret_all(stmts)

        for stmt in stmts:
            if isinstance(stmt, Expression):
                res = self._interpreter.interpret(stmt.expression)
                if res:
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

    def _parse_all(self, tokens: list[Token]) -> list[Stmt]:
        return Parser(tokens, error_reporter=self.parse_error).parse_all()

    def scan_error(self, line: int, message: str) -> None:
        self._report(line, "", message)

    def parse_error(self, token: Token, message: str) -> None:
        self._token_error(token, message)

    def resolution_error(self, token: Token, message: str) -> None:
        self._token_error(token, message)

    def runtime_error(self, error: RuntimeException) -> None:
        sys.stderr.write(f"{str(error)} \n[line {error.token.line}]")
        self._had_runtime_error = True

    def _token_error(self, token: Token, message: str) -> None:
        if token.token_type == TokenType.EOF:
            self._report(token.line, " at the end", message)
        else:
            self._report(token.line, f" at '{token.lexeme}'", message)

    def _report(self, line: int, where: str, message: str):
        sys.stderr.write(f"[line {line}] Error{where}: {message}\n")
        self._had_error = True

    def _handle_errors(self) -> None:
        if self._had_error:
            exit(65)
        if self._had_runtime_error:
            exit(70)


if __name__ == "__main__":
    Pylox().main()
