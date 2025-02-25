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
                "Assign > name: Token, value: Expr",
                "Binary > left: Expr, operator: Token, right: Expr",
                "Call > callee: Expr, paren: Token, arguments: list[Expr]",
                "Grouping > expression: Expr",
                "Literal > value: object",
                "Logical > left: Expr, operator: Token, right: Expr",
                "Unary > operator: Token, right: Expr",
                "Variable > name: Token",
            ],
        )

        self._define_ast(
            output_dir,
            "Stmt",
            [
                "Block > statements: list[Stmt]",
                "Expression > expression: Expr",
                "Function > name: Token, params: list[Token], body: list[Stmt]",
                "If > condition: Expr, then_branch: Stmt, else_branch: Stmt | None",
                "Print > expression: Expr",
                "While > condition: Expr, body: Stmt",
                "Return > keyword: Token, value: Expr | None",
                "Var > name: Token, initializer: Expr | None",
            ],
        )

    def _define_ast(self, output_dir: str, base_name: str, types: list[str]) -> None:
        path = f"{output_dir}/{base_name.lower()}.py"
        with open(path, "w") as f:
            f.writelines(
                [
                    "from dataclasses import dataclass\n",
                    "from abc import ABC, abstractmethod\n",
                    "from typing import TypeVar, Generic\n",
                    "\n",
                    "from app.scanner import Token\n",
                    "\n",
                ]
            )

            self._define_visitor(f, base_name, types)

            f.writelines(
                [
                    f"class {base_name}(ABC):\n",
                    "\t@abstractmethod\n",
                    "\tdef accept(self, visitor: Visitor[R]): ...\n",
                    "\n\n",
                ]
            )

            for concrete_type in types:
                class_name = concrete_type.split(">")[0].strip()
                fields = concrete_type.split(">")[1].strip()
                self._define_type(f, base_name, class_name, fields)

    def _define_visitor(
        self, f: TextIOWrapper, base_name: str, types: list[str]
    ) -> None:
        f.writelines(
            [
                "R = TypeVar('R')",
                "\n\n",
                "class Visitor(Generic[R]):\n",
            ]
        )
        for concrete_type in types:
            class_name = concrete_type.split(">")[0].strip()
            f.writelines(
                [
                    "\t@abstractmethod\n",
                    f"\tdef visit_{class_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: '{class_name}') -> R: ...",
                    "\n\n",
                ]
            )

    def _define_type(
        self, f: TextIOWrapper, base_name: str, class_name: str, fields: str
    ) -> None:
        f.writelines(
            [
                "@dataclass\n",
                f"class {class_name}({base_name}):\n",
                *(f"\t{field.strip()}\n" for field in fields.split(",")),
                "\n",
                "\tdef accept(self, visitor: Visitor[R]) -> R:\n",
                f"\t\treturn visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n",
                "\n\n",
            ]
        )


if __name__ == "__main__":
    GenerateAst().main()
