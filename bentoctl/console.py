import os

from rich.console import Console

console = Console(highlight=False)


def print_generated_files_list(generated_files: list):
    console.print(":sparkles: generated template files.")
    for file in generated_files:
        console.print(f"  - {os.path.join(os.curdir, file)}")
