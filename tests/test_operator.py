import os

from .conftest import TESTOP_PATH


def test_if_testoperator_is_present():
    assert os.path.exists(TESTOP_PATH)
