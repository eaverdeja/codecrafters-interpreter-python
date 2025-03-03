from dataclasses import dataclass

from app.expr import Variable


@dataclass
class VariableRef:
    variable: Variable

    def __hash__(self):
        return id(self.variable)

    def __eq__(self, other):
        if not isinstance(other, VariableRef):
            return False
        return self.variable is other.variable
