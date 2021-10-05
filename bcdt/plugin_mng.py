import os
import json
import sys
import tempfile
import shutil
import zipfile
from urllib.request import urlopen, Request

from rich.pretty import pprint


MASTER_BRANCH = "main"
BCDT_HOME = os.path.expanduser("~/bcdt")
PLUGIN_ACTIONS = ["deploy", "delete", "describe", "update"]


def _get_bcdt_home():
    bcdt_home = os.environ.get("BCDT_HOME", BCDT_HOME)
    # if not present create bcdt and bcdt/plugins dir
    if not os.path.exists(bcdt_home):
        os.mkdir(bcdt_home)
        os.mkdir(os.path.join(bcdt_home, "plugins"))

    return bcdt_home


def _get_plugin_list():
    """
    returns the plugin_list from BCDT_HOME/plugins/plugin_list.json
    """
    bcdt_home = _get_bcdt_home()
    plugin_list_path = os.path.join(bcdt_home, "plugins/plugin_list.json")
    try:
        with open(plugin_list_path, "r") as f:
            plugin_list = json.load(f)
    except FileNotFoundError:
        plugin_list = {}

    return plugin_list


def load_plugin(path):
    pass


def install_plugin(path):
    """
    Adds a new name and path to plugin_list
    """
    bcdt_home = _get_bcdt_home()
    plugin_list_path = os.path.join(bcdt_home, "plugins/plugin_list.json")
    plugin_list = _get_plugin_list()
    print("installing", path)
    with open(plugin_list_path, "w") as f:
        plugin = load_plugin(path=path)
        if plugin.name in plugin_list:
            print(f"Existing {plugin.name} found! Updating...")
        plugin_list[plugin.name] = path
        json.dump(plugin_list, f)


def _remove_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def _github_archive_link(repo_owner, repo_name, repo_branch):
    return f"https://github.com/{repo_owner}/{repo_name}/archive/{repo_branch}.zip"


def _parse_repo_info(github):
    repo_branch = MASTER_BRANCH
    if ":" in github:
        repo_info, repo_branch = github.split(":")
    else:
        repo_info = github
    repo_owner, repo_name = repo_info.split("/")

    return repo_owner, repo_name, repo_branch


def _download_url(url, dest):
    # TODO: setup progess bar with rich
    file_size = None
    req = Request(url)
    u = urlopen(req)
    meta = u.info()
    if hasattr(meta, "getheaders"):
        content_length = meta.getheaders("Content-Length")
    else:
        content_length = meta.get_all("Content-Length")
    if content_length is not None and len(content_length) > 0:
        file_size = int(content_length[0])

    # download to a temporary file and copy it over so that if there is an existing
    # file it doesn't get corrupt.
    dst = os.path.expanduser(dest)
    dst_dir = os.path.dirname(dest)
    f = tempfile.NamedTemporaryFile(delete=False, dir=dst_dir)

    try:
        while True:
            buffer = u.read(8192)
            if len(buffer) == 0:
                break
            f.write(buffer)
        f.close()
        shutil.move(f.name, dst)
    finally:
        f.close()
        if os.path.exists(f.name):
            os.remove(f.name)


def add_plugin(github):
    repo_owner, repo_name, repo_branch = _parse_repo_info(github)
    repo_url = _github_archive_link(repo_owner, repo_name, repo_branch)

    # find default location
    bcdt_home = _get_bcdt_home()
    plugin_home = os.path.join(bcdt_home, "plugins")

    plugin_dir_name = repo_name
    if repo_branch != MASTER_BRANCH:
        plugin_dir_name += f"_{repo_branch}"
    plugin_dir = os.path.join(plugin_home, plugin_dir_name)

    # download the repo as zipfile and extract it
    _download_url(url=repo_url, dest=plugin_dir + ".zip")
    with zipfile.ZipFile(plugin_dir + ".zip", "r") as z:
        if os.path.exists(plugin_dir):
            _remove_if_exists(plugin_dir)
        extracted_repo_name = z.infolist()[0].filename
        z.extractall(plugin_home)
        shutil.move(os.path.join(plugin_home, extracted_repo_name), plugin_dir)
    _remove_if_exists(plugin_dir + ".zip")

    install_plugin(plugin_dir)


def list_plugins():
    plugins_list = _get_plugin_list()
    pprint(plugins_list)
