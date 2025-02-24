import pytest
from dataclasses import dataclass
from typing import Any

from app.exceptions import RuntimeException
from app.environment import Environment


@dataclass
class MockToken:
    """Mock Token class for testing purposes"""

    lexeme: str
    line: int = 1

    def __str__(self) -> str:
        return self.lexeme


@pytest.fixture
def env():
    return Environment()


def test_define_new_variable(env):
    env.define("x", 42)
    assert env.values["x"] == 42


def test_define_overwrite_existing_variable(env):
    env.define("x", 42)
    env.define("x", 100)
    assert env.values["x"] == 100


def test_get_existing_variable(env):
    env.define("x", 42)
    token = MockToken(lexeme="x")
    value = env.get(token)
    assert value == 42


def test_get_undefined_variable_raises_exception(env):
    token = MockToken(lexeme="undefined")
    with pytest.raises(RuntimeException) as excinfo:
        env.get(token)
    assert "Undefined variable 'undefined'" in str(excinfo.value)


def test_assign_existing_variable(env):
    env.define("x", 42)
    token = MockToken(lexeme="x")
    env.assign(token, 100)
    assert env.values["x"] == 100


def test_assign_undefined_variable_raises_exception(env):
    token = MockToken(lexeme="undefined")
    with pytest.raises(RuntimeException) as excinfo:
        env.assign(token, 42)
    assert "Undefined variable 'undefined'" in str(excinfo.value)


@pytest.fixture
def nested_environments():
    global_env = Environment()
    local_env = Environment(enclosing=global_env)
    return global_env, local_env


def test_nested_environments_get(nested_environments):
    global_env, local_env = nested_environments

    # Define variable in global scope
    global_env.define("x", 42)

    # Variable should be accessible from local scope
    token = MockToken(lexeme="x")
    value = local_env.get(token)
    assert value == 42


def test_nested_environments_assign(nested_environments):
    global_env, local_env = nested_environments

    # Define variable in global scope
    global_env.define("x", 42)

    # Assign to variable from local scope
    token = MockToken(lexeme="x")
    local_env.assign(token, 100)

    # Check that the value was updated in the global scope
    assert global_env.values["x"] == 100


def test_nested_environments_shadowing(nested_environments):
    global_env, local_env = nested_environments

    # Define variable in both scopes
    global_env.define("x", 42)
    local_env.define("x", 100)

    # Local scope should get local value
    token = MockToken(lexeme="x")
    value = local_env.get(token)
    assert value == 100

    # Global scope should maintain its value
    value = global_env.get(token)
    assert value == 42


def test_deeply_nested_environments():
    # Setup three levels of environments
    global_env = Environment()
    intermediate_env = Environment(enclosing=global_env)
    local_env = Environment(enclosing=intermediate_env)

    # Define variable in global scope
    global_env.define("x", 42)

    # Variable should be accessible from most nested scope
    token = MockToken(lexeme="x")
    value = local_env.get(token)
    assert value == 42
