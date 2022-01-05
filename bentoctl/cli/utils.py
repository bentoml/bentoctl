import functools
import os
import logging

import cloup

DEBUG_ENV_VAR = "BENTOCTL_DEBUG"


def set_debug_mode(is_enabled: bool):
    if is_enabled or os.environ.get(DEBUG_ENV_VAR):
        os.environ[DEBUG_ENV_VAR] = str(True)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("bentoml").setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)
        logging.getLogger("bentoml").setLevel(logging.WARNING)


class BentoctlCommandGroup(cloup.Group):
    NUMBER_OF_COMMON_PARAMS = 1

    @staticmethod
    def bentoctl_common_params(func):
        @cloup.option(
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
