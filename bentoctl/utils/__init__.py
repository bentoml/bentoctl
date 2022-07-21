import logging
import os

DEBUG_ENV_VAR = "BENTOCTL_DEBUG"


def set_debug_mode(is_enabled: bool):
    if is_enabled or os.environ.get(DEBUG_ENV_VAR):
        os.environ[DEBUG_ENV_VAR] = str(True)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("bentoml").setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger("bentoml").setLevel(logging.WARNING)


def is_debug_mode():
    if DEBUG_ENV_VAR in os.environ:
        return os.environ[DEBUG_ENV_VAR].lower() == "true"
    return False
