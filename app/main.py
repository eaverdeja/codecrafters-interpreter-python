import sys

from app.ast_printer import AstPrinter
from app.expr import Expr
from app.parser import Parser
from app.scanner import Scanner, Token


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
                res = AstPrinter().print(expr)
                print(res)
            case _:
                print(f"Unknown command: {command}", file=sys.stderr)
                exit(1)

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
        res = AstPrinter().print(expr)
        print(res)

    def scan_file(self, filename: str) -> list[Token]:
        with open(filename) as file:
            source = file.read()
        return self._scan(source)

    def parse_file(self, filename: str) -> Expr:
        tokens = self.scan_file(filename)
        return self._parse(tokens)

    def _scan(self, source: str) -> list[Token]:
        scanner = Scanner(source, error_reporter=self.error)
        return scanner.scan_tokens()

    def _parse(self, tokens: list[Token]) -> Expr:
        return Parser(tokens).parse()

    def error(self, line: int, message: str) -> None:
        sys.stderr.write(f"[line {line}] Error: {message}\n")
        self._had_error = True


if __name__ == "__main__":
    Pylox().main()
