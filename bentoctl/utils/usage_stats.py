import os
import uuid
import requests
import yaml

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
        "common_properties": common_properties,
        "event_properties": event_properties,
        "session_id": uuid.uuid1().hex,
        "event_type": "bentoctl-cli"
    }


def track(event_properties: dict):
    if do_not_track():
        return
    payload = get_payload(event_properties=event_properties)

    requests.post(
        USAGE_TRACKING_URL, json=payload, timeout=USAGE_REQUEST_TIMEOUT_SECONDS
    )


def _cli_bentoctl_build_event(cmd_group, cmd_name, cmd_args, cmd_kwargs):
    return {}


cli_events_map = {"cli": {"build": _cli_bentoctl_build_event}}
# {
#     'session_id': 'e0511c1ac5a711ecbc9f1c5c60561cbc',
#     'event_properties': {
#         'cmd_name': 'serve',
#         'error_type': None,
#         'return_code': None
#     },
#     'common_properties': {
#         'timestamp': '2022-04-26T21:28:59.408329+00:00',
#         'platform': 'Darwin-21.5.0-x86_64-i386-64bit',
#         'bentoml_version': '1.0.0a7.post9+gea0040f3',
#         'python_version': '3.7.10',
#          'is_interactive': False, 'in_notebook': False, 'memory_usage_percent': 0.6437778472900391, 'total_memory_in_mb': 16384,
#          'client': {
#              'id': '0cf269e4-ecf7-4869-ba7f-f32bc3d39ee5',
#              'creation_timestamp': '2022-04-06T22:14:53.694582+00:00'
#         },
#         'yatai_user_email': 'admin@abc.com'
#     },
#     'event_type': 'cli'
# }