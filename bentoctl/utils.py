import os
import shutil
import os.path
import tempfile

from rich.table import Table

from bentoctl.console import console
from bentoctl.operator.utils import fetch_git_info


def is_debug_mode():
    return bool(os.environ.get("BENTOCTL_DEBUG"))


def print_operator_list(operator_list):
    if is_debug_mode():
        console.print(operator_list)
    table = Table("Name", "Location", box=None)

    for name, info in operator_list.items():
        if info.get("git_url") is not None:
            owner, repo = fetch_git_info(info["git_url"])
            location_str = f"{owner}/{repo} ({info['git_branch']})"
            table.add_row(name, location_str)
        else:
            location_str = os.path.join(
                "$HOME", os.path.relpath(info["path"], os.path.expanduser("~"))
            )
            table.add_row(name, location_str)

    console.print(table)

class TempDirectory(object):
    """
    Helper class that creates and cleans up a temporary directory, can
    be used as a context manager.
    >>> with TempDirectory() as tempdir:
    >>>     print(os.path.isdir(tempdir))
    """

    def __init__(
        self,
        cleanup=True,
        prefix="temp",
    ):

        self._cleanup = cleanup
        self._prefix = prefix
        self.path = None

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.path)

    def __enter__(self):
        self.create()
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cleanup:
            self.cleanup()

    def create(self):
        if self.path is not None:
            return self.path

        tempdir = tempfile.mkdtemp(prefix="bentoctl-{}-".format(self._prefix))
        self.path = os.path.realpath(tempdir)

    def cleanup(self, ignore_errors=False):
        """
        Remove the temporary directory created
        """
        if self.path is not None and os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=ignore_errors)
        self.path = None
