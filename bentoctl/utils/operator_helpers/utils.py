from __future__ import annotations

import json
import subprocess
from shutil import which


def run_shell_command(
    command: list[str],
    cwd: str | None = None,
    env: dict | None = None,
    shell_mode: bool = False,
):
    exec_path = which(command[0])
    proc = subprocess.Popen(
        exec_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode,
        cwd=cwd,
        env=env,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        try:
            return json.loads(stdout.decode("utf-8")), stderr.decode("utf-8")
        except json.JSONDecodeError:
            return stdout.decode("utf-8"), stderr.decode("utf-8")
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode("utf-8")}'
        )
