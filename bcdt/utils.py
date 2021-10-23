from datetime import datetime

from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


def show_time_diff(dt: datetime):
    pass


def print_deployments_list(d_list):
    table = Table(title="", box=box.SIMPLE)

    table.add_column("Deployment Name")
    table.add_column("Operator")
    table.add_column("Last Updated")

    for d in d_list:
        table.add_row(
            d.deployment_name, d.operator_name, d.created_at.strftime("%H:%M")
        )
    console.print(table)
