import os
import typing as t
import shutil
from pathlib import Path

from bentoctl.operator import utils


def test_bentoctl_home_dir(tmp_path):
    assert utils._get_bentoctl_home() == Path(os.path.expanduser("~/bentoctl"))

    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    bcdt_home = utils._get_bentoctl_home()
    assert bcdt_home == tmp_path

    assert (tmp_path / "operators").exists()


class RepoCopy:
    def __init__(self, path):
        self.git_repo_path = Path(path)
        self.git = t.SimpleNamespace()
        self.git.checkout = self.checkout

    @classmethod
    def clone_from(cls, src_path, repo_path):
        shutil.copytree(src_path, repo_path)
        return cls(repo_path)

    def checkout(self, branch):
        (self.git_repo_path / branch).touch()
        return branch
