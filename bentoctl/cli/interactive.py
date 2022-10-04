from collections import OrderedDict

from cerberus import Validator
from rich.control import Control
from rich.segment import ControlType, SegmentLines

from bentoctl.console import console
from bentoctl.deployment_config import DeploymentConfig, deployment_config_schema
from bentoctl.operator import get_local_operator_registry

local_operator_registry = get_local_operator_registry()


INTERACTIVE_MODE_TITLE = "[r]Bentoctl Interactive Deployment Config Builder[/]"
WELCOME_MESSAGE = """
[green]Welcome![/] You are now in interactive mode.

This mode will help you setup the deployment_config.yaml file required for
deployment. Fill out the appropriate values for the fields.

[dim](deployment config will be saved to: ./deployment_config.yaml)[/]
"""


class PromptMsg:
    def __init__(self, help_msg, val_error=None):
        self.help_msg = help_msg
        self.val_error = val_error

    def __rich_console__(self, rconsole, options):  # pylint: disable=unused-argument
        if self.help_msg is not None:
            yield f"[grey50]Help: {self.help_msg}[/]"
        if self.val_error is not None:
            yield f"[red]Validation Error: {self.val_error}[/]"


def clear_console(num_lines):
    """
    clear console message base on the given line count
    """
    console.print(
        Control(
            ControlType.CARRIAGE_RETURN,
            (ControlType.ERASE_IN_LINE, 2),
            *(
                (
                    (ControlType.CURSOR_UP, 1),
                    (ControlType.ERASE_IN_LINE, 2),
                )
                * num_lines
            ),
        )
    )


class display_console_message:
    """
    Display a message on the console, and clear it after user exits out of the block

    Usage:
        with display_console_message("This is a message"):
            # do something
    """

    def __init__(self, message, should_render_message=True):
        self.message = message
        self.should_render_message = should_render_message
        self.message_lines = console.render_lines(self.message)
        self.clean_up = True
        self.line_needed_to_clear = len(self.message_lines)

    def __enter__(self):
        if self.should_render_message:
            console.print(SegmentLines(self.message_lines, new_lines=True))

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_console(self.line_needed_to_clear)


def prompt_input_value(field_name, rule):
    """
    console prompt for input value from user. Display error message if validation fails
    clean up the prompt message and/or error message afterward.
    """
    validator = Validator()
    help_message = rule.pop("help_message", None)
    default_value = rule.get("default", None)
    validation_error_message = None
    suffix = f" [[b]{default_value}[/]]: " if default_value is not None else ": "
    input_message = (
        f"{field_name}{suffix}" if field_name != "" else "Enter your input: "
    )
    while True:
        with display_console_message(PromptMsg(help_message, validation_error_message)):
            user_input_value = console.input(input_message)
            clear_console(1)
        user_input_value = user_input_value if user_input_value != "" else None
        validated_field = validator.validated(
            {field_name: user_input_value}, schema={field_name: rule}
        )
        if validated_field is None:
            validation_error_message = ". ".join(validator.errors[field_name])
        else:
            return validated_field[field_name]


def prompt_confirmation(message):
    """
    This will prompt the user with y/n question. Before the function returns
    value, it will clear up all of the prompt messages and error messages.

    Return boolean value
    """
    error_message = "Please enter yes or no"
    line_to_clear = 0
    input_message = f"{message} [b](y/n)[/]: "
    message_line_count = len(console.render_lines(input_message))
    while True:
        result = console.input(input_message)
        line_to_clear += message_line_count
        if result.lower() == "y" or result.lower() == "yes":
            clear_console(line_to_clear)
            return True
        elif result.lower() == "n" or result.lower() == "no":
            clear_console(line_to_clear)
            return False
        else:
            console.print(error_message)
            line_to_clear += 1


def prompt_input(
    field_name, rule, indent_level=1, belongs_to_list=False, require_display_dash=False
):
    """
    Need to handle cases:
        foo: bar,
        foo: [bar, baz]
        foo: {bar: baz}
        foo: {bar: [baz, qux]}
        foo: {bar: [{baz: qux}, {qux: qux}]}

    Returns the user input value
    """
    # TODO: better display for the case of foo: [bar, baz].  Right now the console
    #  prompt will display `: your_input`
    input_value = None
    if rule.get("type") == "list":
        indented_print(f"{field_name}:", indent_level)
        input_value = []
        if rule.get("required") is not True:
            should_add_item_to_list = prompt_confirmation(
                f"Do you want to add item to {field_name}"
            )
        else:
            should_add_item_to_list = (
                True  # user should be able to add at least one item
            )
        while should_add_item_to_list:
            value = prompt_input("", rule["schema"], indent_level, True, True)
            input_value.append(value)
            should_add_item_to_list = prompt_confirmation(
                f"Do you want to add another item to {field_name}"
            )
        if not input_value:
            input_value = None
    elif rule.get("type") == "dict":
        input_value = {}
        if not belongs_to_list:
            indented_print(f"{field_name}:", indent_level)
            if "schema" in rule:
                for key in rule["schema"].keys():
                    input_value[key] = prompt_input(
                        key, rule["schema"].get(key, {}), indent_level + 1
                    )
            else:
                # We don't have a schema so this is a dict with arbitrary keys.
                help_message = rule.get("help_message")
                with display_console_message(PromptMsg(help_message, None)):
                    should_add_item_to_dict = prompt_confirmation(
                        f"Do you want to add item to {field_name}"
                    )
                while should_add_item_to_dict:
                    key = prompt_input_value("key", rule.get("keysrules", {}))
                    value = prompt_input_value("value", rule.get("valuesrules", {}))
                    display_input_result = f"{key}: {value}"
                    indented_print(display_input_result, indent_level=indent_level + 1)
                    input_value[key] = value

                    with display_console_message(PromptMsg(help_message, None)):
                        should_add_item_to_dict = prompt_confirmation(
                            f"Do you want to add item to {field_name}"
                        )
        else:
            for i, key in enumerate(rule["schema"].keys()):
                input_value[key] = prompt_input(
                    key,
                    rule["schema"].get(key, {}),
                    indent_level,
                    belongs_to_list,
                    i == 0,  # require display '-' for first item of a dict
                )
        input_value = dict((k, v) for k, v in input_value.items() if v is not None)
    else:
        input_value = prompt_input_value(field_name, rule)
        if belongs_to_list:
            if require_display_dash:
                if field_name:
                    display_input_result = f"- {field_name}: {input_value}"
                else:
                    display_input_result = f"- {input_value}"
            else:
                display_input_result = f"  {field_name}: {input_value}"
        else:
            display_input_result = f"{field_name}: {input_value}"
        indented_print(display_input_result, indent_level=indent_level)
    return input_value


def indented_print(message, indent_level=0):
    """
    print the message with indentation
    """
    indent_level = "    " * indent_level  # 4 spaces for each indentation level
    console.print(indent_level, end="")
    console.print(message)


def generate_spec(schema):
    spec = OrderedDict()

    for field, rule in schema.items():
        val = prompt_input(field, rule)
        if val:  # only update with non-empty value
            spec.update({field: val})

    return spec


def dropdown_select(field: str, options: list):
    """
    interactive menu to select operator
    """
    try:
        from simple_term_menu import TerminalMenu

        tmenu = TerminalMenu(options, title="Choose an operator")
        choice = tmenu.show()
        return options[choice]
    except ImportError:
        operator = prompt_input_value(field, deployment_config_schema.get(field))

        return operator


def deployment_config_builder():
    """
    Interactively build the deployment config.
    """
    deployment_config = {
        "api_version": "v1",
    }

    console.print(INTERACTIVE_MODE_TITLE)
    console.print(WELCOME_MESSAGE)
    console.print("[b]api_version:[/] v1")

    # get deployment name
    name = prompt_input_value("name", deployment_config_schema.get("name"))
    deployment_config["name"] = name
    console.print(f"[b]name:[/] {name}")

    # get operators
    available_operators = list(local_operator_registry.list())
    operator_name = (
        available_operators[0]
        if len(available_operators) == 1
        else dropdown_select("operator", available_operators)
    )
    indented_print("[b]operator:[/]")
    indented_print(f"[b]name:[/] {operator_name}", indent_level=1)
    deployment_config["operator"] = {"name": operator_name}
    operator = local_operator_registry.get(operator_name)

    # get template_type
    template_name = (
        operator.default_template
        if len(operator.available_templates) == 1
        else dropdown_select("template", operator.available_templates)
    )
    deployment_config["template"] = template_name
    console.print(f"[b]template:[/] {template_name}")

    console.print("[bold]spec: [/]")
    spec = generate_spec(operator.schema)
    deployment_config["spec"] = dict(spec)

    env = prompt_input("[b]env", deployment_config_schema.get("env"), indent_level=0)
    deployment_config["env"] = dict(env)

    return DeploymentConfig(deployment_config)
