import os
import json
import tempfile
import shutil
import zipfile
from collections import namedtuple
from urllib.request import urlopen, Request

from rich.pretty import pprint

from .plugin_loader import Plugin
from . import BCDT_HOME


MAIN_BRANCH = "deployers"
OFFICIAL_PLUGINS = {"aws-lambda": "jjmachan/aws-lambda-deploy:deployers"}

github_repo = namedtuple("github_repo", ["owner", "name", "branch"])


def _get_bcdt_home():
    bcdt_home = os.environ.get("BCDT_HOME", BCDT_HOME)
    # if not present create bcdt and bcdt/plugins dir
    if not os.path.exists(bcdt_home):
        os.mkdir(bcdt_home)
        os.mkdir(os.path.join(bcdt_home, "plugins"))

    return bcdt_home


def get_plugin_list():
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


def install_plugin(path):
    """
    Adds a new name and path to plugin_list
    """
    bcdt_home = _get_bcdt_home()
    plugin_list_path = os.path.join(bcdt_home, "plugins/plugin_list.json")
    plugin_list = get_plugin_list()
    print("installing", path)
    with open(plugin_list_path, "w") as f:
        plugin = Plugin(path)
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


def _parse_github_url(github_url):
    repo_branch = MAIN_BRANCH
    if ":" in github_url:
        repo_info, repo_branch = github_url.split(":")
    else:
        repo_info = github_url
    repo_owner, repo_name = repo_info.split("/")

    return github_repo(repo_owner, repo_name, repo_branch)


def _parse_repo_info(github):
    """
    Parse the plugin name that the user has given. Options to consider:
        1. Official plugin - only the plugin name is needed in this case
        2. Github Repo - this should be in the format 'repo_owner/repo_name:repo_branch'

    TODO:
        1. https://, git://, http://
    """
    # figure out how the user has passed the plugin
    # TODO: verify with patterns.
    if github in OFFICIAL_PLUGINS.keys():
        github_url = OFFICIAL_PLUGINS[github]
        github_repo = _parse_github_url(github_url)
        plugin_name = github
    else:
        github_repo = _parse_github_url(github)
        plugin_name = github_repo.name

    if github_repo.branch != MAIN_BRANCH:
        plugin_name += f":{github_repo.repo_branch}"

    return github_repo, plugin_name


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
    github_repo, plugin_name = _parse_repo_info(github)
    repo_url = _github_archive_link(
        github_repo.owner, github_repo.name, github_repo.branch
    )
    print(repo_url)

    # find default location
    bcdt_home = _get_bcdt_home()
    plugin_home = os.path.join(bcdt_home, "plugins")

    # the plugin's name is its directory name
    plugin_dir_name = plugin_name
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
    plugins_list = get_plugin_list()
    pprint(plugins_list)
