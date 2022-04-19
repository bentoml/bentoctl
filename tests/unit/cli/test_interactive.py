import sys
from contextlib import redirect_stdout
from io import StringIO

import pytest

import bentoctl
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
def test_select_operator(mock_terminal_menu, monkeypatch):

    monkeypatch.setattr(
        interactive_cli.local_operator_registry, "list", lambda: ["op1", "op2"]
    )
    assert interactive_cli.select_operator() == "op2"

    # with only one
    monkeypatch.setattr(
        interactive_cli.local_operator_registry, "list", lambda: ["op2"]
    )
    assert interactive_cli.select_operator() == "op2"


@pytest.mark.skipif(sys.platform.startswith("win"), reason="don't work for windows")
def test_select_template_type(mock_terminal_menu):
    assert interactive_cli.select_template_type(["template1"]) == "template1"
    assert (
        interactive_cli.select_template_type(["template1", "template2"]) == "template2"
    )


@pytest.mark.parametrize("indent_level", [0, 1, 2])
def test_inteneded_print(indent_level):
    f = StringIO()
    with redirect_stdout(f):
        interactive_cli.intended_print("test_message", indent_level=indent_level)
        assert f.getvalue() == f"{'    '*indent_level}test_message\n"


def test_deployment_config_builder(
    monkeypatch, get_mock_operator_registry, mock_operator
):
    operator1 = mock_operator(name="operator1", schema={})
    get_mock_operator_registry.get = lambda _: operator1
    stdin = StringIO("testdeployment\n")
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr(interactive_cli, "select_operator", lambda: "operator1")
    monkeypatch.setattr(interactive_cli, "select_template_type", lambda types: types[0])
    monkeypatch.setattr(
        interactive_cli, "local_operator_registry", get_mock_operator_registry
    )
    monkeypatch.setattr(
        "bentoctl.deployment_config.local_operator_registry", get_mock_operator_registry
    )
    interactive_cli.deployment_config_builder()
