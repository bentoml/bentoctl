import sys
from contextlib import redirect_stdout
from io import StringIO

import pytest

import bentoctl.cli.interactive as interactive_cli


class MockTerminalMenu:
    def __init__(self, options, title) -> None:
        self.available_ops = options

    def show(self):
        return -1


@pytest.fixture()
def mock_terminal_menu(monkeypatch):
    import simple_term_menu

    monkeypatch.setattr(simple_term_menu, "TerminalMenu", MockTerminalMenu)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="don't work for windows")
def test_dropdown_select(mock_terminal_menu):
    assert interactive_cli.dropdown_select("field", ["template1"]) == "template1"
    assert (
        interactive_cli.dropdown_select("field", ["template1", "template2"])
        == "template2"
    )


@pytest.mark.parametrize("indent_level", [0, 1, 2])
def test_inteneded_print(indent_level):
    f = StringIO()
    with redirect_stdout(f):
        interactive_cli.indented_print("test_message", indent_level=indent_level)
        assert f.getvalue() == f"{'    '*indent_level}test_message\n"


def test_deployment_config_builder(
    monkeypatch, get_mock_operator_registry, mock_operator
):
    operator1 = mock_operator(name="operator1", schema={})
    get_mock_operator_registry.get = lambda _: operator1
    stdin = StringIO("testdeployment\ny\nBENTOML_API_WORKERS\n1\nn\n")
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr(
        interactive_cli, "dropdown_select", lambda field, options: "operator1"
    )
    monkeypatch.setattr(
        interactive_cli, "local_operator_registry", get_mock_operator_registry
    )
    monkeypatch.setattr(
        "bentoctl.deployment_config.local_operator_registry", get_mock_operator_registry
    )
    interactive_cli.deployment_config_builder()


list_of_strings = {
    "rule": {"type": "list", "schema": {"type": "string"}},
    "user_input": "y\nhai\ny\nhai\nn\n",
    "expected_output": ["hai", "hai"],
}

list_of_strings_required = {
    "rule": {"type": "list", "required": True, "schema": {"type": "string"}},
    "user_input": "hai\ny\nhai\nn\n",
    "expected_output": ["hai", "hai"],
}

list_of_strings_required_with_nested_dict = {
    "rule": {
        "type": "list",
        "required": True,
        "schema": {"type": "dict", "schema": {"string": {"type": "string"}}},
    },
    "user_input": "name\ny\nname\nn\n",
    "expected_output": [{"string": "name"}, {"string": "name"}],
}

nested_dict = {
    "rule": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "list": {"type": "list", "schema": {"type": "string"}},
            "dict": {"type": "dict", "schema": {"name": {"type": "string"}}},
        },
    },
    "user_input": "name\ny\nitem1\ny\nitem2\nn\ndict_name\n",
    "expected_output": {
        "name": "name",
        "list": ["item1", "item2"],
        "dict": {"name": "dict_name"},
    },
}

single_map = {
    "rule": {
        "type": "dict",
        "keysrules": {"type": "string"},
        "valuesrules": {"type": "integer", "coerce": int},
    },
    "user_input": "y\nkey_1\n1\ny\nkey_2\n2\nn",
    "expected_output": {
        "key_1": 1,
        "key_2": 2,
    },
}

all_values = {
    "rule": {
        "type": "dict",
        "schema": {
            "int": {"type": "integer", "coerce": int},
            "float": {"type": "float", "coerce": float},
            "bool": {"type": "boolean", "coerce": bool},
        },
    },
    "user_input": "120\n120.23\nTrue",
    "expected_output": {"int": 120, "float": 120.23, "bool": True},
}


@pytest.mark.parametrize(
    "test_case",
    [
        list_of_strings,
        list_of_strings_required,
        list_of_strings_required_with_nested_dict,
        nested_dict,
        single_map,
        all_values,
    ],
)
def test_prompt_input(monkeypatch, test_case):
    stdin = StringIO(test_case["user_input"])
    monkeypatch.setattr("sys.stdin", stdin)
    output = interactive_cli.prompt_input("test", test_case["rule"])
    assert output == test_case["expected_output"]
