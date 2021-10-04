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


def _get_bcdt_home():
    bcdt_home = os.environ.get("BCDT_HOME", BCDT_HOME)
    # if not present create bcdt and bcdt/deployers dir
    if not os.path.exists(bcdt_home):
        os.mkdir(bcdt_home)
        os.mkdir(os.path.join(bcdt_home, "deployers"))

    return bcdt_home


def import_module(name, path):
    import importlib.util
    from importlib.abc import Loader

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert isinstance(spec.loader, Loader)
    spec.loader.exec_module(module)
    return module


def _get_deployer_list():
    """
    returns the deployer_list from BCDT_HOME/deployers/deployer_list.json
    """
    bcdt_home = _get_bcdt_home()
    deployer_list_path = os.path.join(bcdt_home, "deployers/deployer_list.json")
    try:
        with open(deployer_list_path, "r") as f:
            deployer_list = json.load(f)
    except FileNotFoundError:
        deployer_list = {}

    return deployer_list


def load_deployer(name='', path=None):
    """
    Load the deployer given a name or path. If name is given it loads it from the
    deployer_list. If path is given it loads it from the given path
    """
    if name:
        deployer_list = _get_deployer_list()
        deployer_path = deployer_list[name]
    elif path:
        deployer_path = path
    else:
        raise ValueError("Atleast one named argument must be provided but not both.")

    # import the deployer
    sys.path.append(deployer_path)
    deployer = import_module(name, os.path.join(deployer_path, "deployer_conf.py"))
    sys.path.remove(deployer_path)

    return deployer


def install_deployer(path):
    """
    Adds a new name and path to deployer_list
    """
    bcdt_home = _get_bcdt_home()
    deployer_list_path = os.path.join(bcdt_home, "deployers/deployer_list.json")
    deployer_list = _get_deployer_list()
    print('installing', path)
    with open(deployer_list_path, "w") as f:
        deployer = load_deployer(path=path)
        if deployer.name in deployer_list:
            print(f"Existing {deployer.name} found! Updating...")
        deployer_list[deployer.name] = path
        json.dump(deployer_list, f)


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


def add_deployer(github):
    repo_owner, repo_name, repo_branch = _parse_repo_info(github)
    repo_url = _github_archive_link(repo_owner, repo_name, repo_branch)

    # find default location
    bcdt_home = _get_bcdt_home()
    deployer_home = os.path.join(bcdt_home, "deployers")

    deployer_dir_name = repo_name
    if repo_branch != MASTER_BRANCH:
        deployer_dir_name += f"_{repo_branch}"
    deployer_dir = os.path.join(deployer_home, deployer_dir_name)

    # download the repo as zipfile and extract it
    _download_url(url=repo_url, dest=deployer_dir + ".zip")
    with zipfile.ZipFile(deployer_dir + ".zip", "r") as z:
        if os.path.exists(deployer_dir):
            _remove_if_exists(deployer_dir)
        extracted_repo_name = z.infolist()[0].filename
        z.extractall(deployer_home)
        shutil.move(os.path.join(deployer_home, extracted_repo_name), deployer_dir)
    _remove_if_exists(deployer_dir + ".zip")

    install_deployer(deployer_dir)


def list_deployers():
    deployers_list = _get_deployer_list()
    pprint(deployers_list)
