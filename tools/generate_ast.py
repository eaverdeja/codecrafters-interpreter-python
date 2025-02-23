from io import TextIOWrapper
import sys


class GenerateAst:
    def main(self) -> None:
        if len(sys.argv) != 2:
            print(
                "Usage: ./your_program.sh generate_ast <output directory>",
                file=sys.stderr,
            )
            exit(1)

        output_dir = sys.argv[1]
        self._define_ast(
            output_dir,
            "Expr",
            [
                "Binary | left: Expr, operator: Token, right: Expr",
                "Literal | value: object",
            ],
        )

    def _define_ast(self, output_dir: str, base_name: str, types: list[str]) -> None:
        path = f"{output_dir}/{base_name.lower()}.py"
        with open(path, "w") as f:
            f.writelines(
                [
                    "from dataclasses import dataclass\n",
                    "from abc import ABC\n",
                    "\n",
                    "from app.scanner import Token\n",
                    "\n",
                    "\n",
                    f"class {base_name}(ABC): ...\n",
                    "\n\n",
                ]
            )

            for concrete_type in types:
                class_name = concrete_type.split("|")[0].strip()
                fields = concrete_type.split("|")[1].strip()
                self._define_type(f, base_name, class_name, fields)

    def _define_type(
        self, f: TextIOWrapper, base_name: str, class_name: str, fields: str
    ) -> None:
        f.writelines(
            [
                "@dataclass\n",
                f"class {class_name}({base_name}):\n",
                *(f"\t{field.strip()}\n" for field in fields.split(",")),
                "\n\n",
            ]
        )


if __name__ == "__main__":
    GenerateAst().main()
