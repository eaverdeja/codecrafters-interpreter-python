from dataclasses import dataclass


@dataclass
class LoxClass:
    name: str

    def __str__(self) -> str:
        return self.name
