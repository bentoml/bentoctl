import functools
import os

import cloup

DEBUG_ENV_VAR = "BENTOCTL_DEBUG"


def set_debug_mode(enabled: bool):
    os.environ[DEBUG_ENV_VAR] = str(enabled)


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
            if verbose:
                set_debug_mode(True)

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
