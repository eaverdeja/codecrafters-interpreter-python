import sys

from app.scanner import Scanner


class Pylox:
    _had_error = False

    def main(self) -> None:
        if len(sys.argv) == 1:
            self.run_prompt()
            exit(0)

        if len(sys.argv) < 3:
            print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
            exit(1)

        command = sys.argv[1]
        filename = sys.argv[2]

        if command != "tokenize":
            print(f"Unknown command: {command}", file=sys.stderr)
            exit(1)

        self.run_file(filename)

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
        scanner = Scanner(source, error_reporter=self.error)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    def error(self, line: int, message: str) -> None:
        sys.stderr.write(f"[line {line}] Error: {message}\n")
        self._had_error = True


if __name__ == "__main__":
    Pylox().main()
