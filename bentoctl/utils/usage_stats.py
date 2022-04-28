import os
import uuid
import requests
import yaml

# These are internal apis. We will need to make sure update these when BentoML changes.
from bentoml._internal.utils import bentoml_cattr
from bentoml._internal.utils.analytics.schemas import CommonProperties


BENTOCTL_DO_NOT_TRACK = "BENTOML_DO_NOT_TRACK"
USAGE_TRACKING_URL = "https://t.bentoml.com"
USAGE_REQUEST_TIMEOUT_SECONDS = 1


def do_not_track() -> bool:
    # Returns True if and only if the environment variable is defined and has value True.
    # The function is cached for better performance.
    return os.environ.get(BENTOCTL_DO_NOT_TRACK, str(False)).lower() == "true"


def get_payload(event_properties: dict) -> dict:
    common_properties = CommonProperties()
    return {
        "common_properties": bentoml_cattr.unstructure(common_properties),
        "event_properties": event_properties,
        "session_id": uuid.uuid1().hex,
        "event_type": "bentoctl-cli",
    }


def track(event_properties):
    if do_not_track():
        return
    payload = get_payload(event_properties=vars(event_properties))

    requests.post(
        USAGE_TRACKING_URL, json=payload, timeout=USAGE_REQUEST_TIMEOUT_SECONDS
    )


class CliEvent:
    def __init__(
        self,
        cmd_group,
        cmd_name,
        duration_in_ms=None,
        error_type=None,
        return_code=None,
        operator=None,
        version=None,
    ):
        self.cmd_group = cmd_group
        self.cmd_name = cmd_name
        self.duration_in_ms = duration_in_ms
        self.error_type = error_type
        self.return_code = return_code
        self.operator = operator
        self.version = version


def _bentoctl_event(cmd_group, cmd_name, return_value=None):
    if return_value is not None:
        deployment_config = return_value
        version = (
            deployment_config.bento.tag.version if deployment_config.bento else None
        )

        return CliEvent(
            cmd_group,
            cmd_name,
            operator=deployment_config.operator_name,
            version=version,
        )
    else:
        return CliEvent(cmd_group, cmd_name)


cli_events_map = {"bentoctl": _bentoctl_event}
