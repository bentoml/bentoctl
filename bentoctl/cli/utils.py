from __future__ import annotations

import functools
import os
import sys
import time

import click

from bentoctl.exceptions import BentoctlException
from bentoctl.utils import set_debug_mode
from bentoctl.utils.usage_stats import (
    BENTOML_DO_NOT_TRACK,
    BentoctlCliEvent,
    cli_events_map,
    track,
)

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


class BentoctlCommandGroup(click.Group):
    NUMBER_OF_COMMON_PARAMS = 2

    @staticmethod
    def bentoctl_common_params(func):
        @click.option(
            "--verbose",
            "--debug",
            is_flag=True,
            default=False,
            help="Show debug logs when running the command",
        )
        @click.option(
            "--do-not-track",
            is_flag=True,
            default=False,
            envvar=BENTOML_DO_NOT_TRACK,
            help="Do not send uage info",
        )
        @functools.wraps(func)
        def wrapper(verbose, *args, **kwargs):
            set_debug_mode(verbose)

            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def bentoctl_track_usage(func, cmd_group, **kwargs):
        command_name = kwargs.get("name", func.__name__)

        @functools.wraps(func)
        def wrapper(do_not_track: bool, *args, **kwargs):
            if do_not_track:
                os.environ["BENTOCTL_DO_NOT_TRACK"] = str(True)
                return func(*args, **kwargs)
            start_time = time.time_ns()
            if cmd_group.name in cli_events_map:
                # If cli command is build or operator related, we will add
                # additoinal properties
                get_tracking_event = functools.partial(
                    cli_events_map[cmd_group.name],
                    cmd_group.name,
                    command_name,
                )
            elif cmd_group.name == "operator":

                def get_tracking_event(_):  # pylint: disable=unused-argument
                    return BentoctlCliEvent(
                        cmd_group.name, command_name, operator=kwargs.get("name", None)
                    )

            else:

                def get_tracking_event(_):  # pylint: disable=unused-argument
                    return BentoctlCliEvent(cmd_group.name, command_name)

            try:
                return_value = func(*args, **kwargs)
                event = get_tracking_event(return_value)
                duration_in_ms = time.time_ns() - start_time
                event.duration_in_ms = duration_in_ms / 1e6
                track(event)
                return return_value
            except Exception as e:
                event = get_tracking_event(None)
                duration_in_ms = time.time_ns() - start_time
                event.duration_in_ms = duration_in_ms / 1e6
                event.error_type = type(e).__name__
                event.return_code = 2 if isinstance(e, KeyboardInterrupt) else 1
                track(event)
                raise

        return wrapper

    def command(self, *args, **kwargs):
        def wrapper(func):
            # add common parameters to command
            func = BentoctlCommandGroup.bentoctl_common_params(func)
            func = BentoctlCommandGroup.bentoctl_track_usage(func, self, **kwargs)

            # move common parameters to end of the parameters list
            func.__click_params__ = (
                func.__click_params__[-self.NUMBER_OF_COMMON_PARAMS :]
                + func.__click_params__[: -self.NUMBER_OF_COMMON_PARAMS]
            )
            return super(BentoctlCommandGroup, self).command(*args, **kwargs)(func)

        return wrapper
