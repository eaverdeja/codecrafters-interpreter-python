from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.lox_class import LoxClass


@dataclass
class LoxInstance:
    klass: "LoxClass"

    def __str__(self):
        return f"{self.klass} instance"
