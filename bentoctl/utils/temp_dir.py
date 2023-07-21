import os
import shutil
import tempfile
from pathlib import Path


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

    def __enter__(self) -> Path:
        return Path(self.create())

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cleanup:
            self.cleanup()

    def create(self) -> str:
        if self.path is not None:
            return self.path

        tempdir = tempfile.mkdtemp(prefix="bentoctl-{}-".format(self._prefix))
        self.path = os.path.realpath(tempdir)
        return self.path

    def cleanup(self, ignore_errors=False):
        """
        Remove the temporary directory created
        """
        if self.path is not None and os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=ignore_errors)
        self.path = None
