import functools
import logging
import os
import sys

import click

from bentoctl.exceptions import BentoctlException

DEBUG_ENV_VAR = "BENTOCTL_DEBUG"


def handle_bentoctl_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BentoctlException as error:
            error.show()
            sys.exit(0)

    return wrapper


def set_debug_mode(is_enabled: bool):
    if is_enabled or os.environ.get(DEBUG_ENV_VAR):
        os.environ[DEBUG_ENV_VAR] = str(True)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("bentoml").setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger("bentoml").setLevel(logging.WARNING)


class BentoctlCommandGroup(click.Group):
    NUMBER_OF_COMMON_PARAMS = 1

    @staticmethod
    def bentoctl_common_params(func):
        @click.option(
            "--verbose",
            "--debug",
            is_flag=True,
            default=False,
            help="Show debug logs when running the command",
        )
        @functools.wraps(func)
        def wrapper(verbose, *args, **kwargs):
            set_debug_mode(verbose)

            return func(*args, **kwargs)

        return wrapper

    def command(self, *args, **kwargs):
        def wrapper(func):
            # add common parameters to command
            func = BentoctlCommandGroup.bentoctl_common_params(func)

            # move common parameters to end of the parameters list
            func.__click_params__ = (
                func.__click_params__[-self.NUMBER_OF_COMMON_PARAMS :]
                + func.__click_params__[: -self.NUMBER_OF_COMMON_PARAMS]
            )
            return super(BentoctlCommandGroup, self).command(*args, **kwargs)(func)

        return wrapper
