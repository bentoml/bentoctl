# pylint: disable=W0621
import os

import pytest
from click.testing import CliRunner

import bentoctl
from bentoctl import __version__, deployment_config
from bentoctl.cli import bentoctl as bentoctl_cli
from bentoctl.operator import get_local_operator_registry
from tests.conftest import TESTOP_PATH

TEST_DEPLOYMENT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "test_deployment_config.yaml"
)


@pytest.fixture
def op_reg_with_testop(tmp_path, monkeypatch):
    op_reg_path = tmp_path / "operator_registry"

    # patch get_bento_path
    monkeypatch.setattr(deployment_config, "get_bento_path", lambda x: x)

    # patched operator registry with testop added
    os.environ["BENTOCTL_HOME"] = str(op_reg_path)
    op_reg = get_local_operator_registry()
    op_reg.add(TESTOP_PATH)
    monkeypatch.setattr(deployment_config, "local_operator_registry", op_reg)

    yield op_reg

    del os.environ["BENTOCTL_HOME"]


def test_bentoctl_version():
    runner = CliRunner()
    result = runner.invoke(bentoctl_cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


class DeploymentConfigMock:
    @classmethod
    def from_file(cls, file):
        return cls()

    def save(self, save_path, filename):
        pass

    def set_bento(self, tag):
        pass

    def generate(self, destination_dir=None, values_only=False):
        if values_only:
            return ["bentoctl.tfvars"]
        else:
            return ["main.tf", "bentoctl.tfvars"]

    def generate_local_image_tag(self):
        return "local_image_tag"

    def create_deployable(self, destination_dir=None):
        return "dockerfile_path", "docker_context_path", "build_args"

    def get_registry_info(self):
        return "registry_url", "registry_username", "registry_pass"

    def generate_docker_image_tag(self, registry_url):
        return "repository_image_tag"


def test_cli_init(monkeypatch, tmp_path):
    monkeypatch.setattr(
        bentoctl.cli,
        "deployment_config_builder",
        lambda: DeploymentConfigMock(),
    )
    runner = CliRunner()

    # vanila init
    with runner.isolated_filesystem():
        result = runner.invoke(
            bentoctl_cli, ["init"], input="\n", catch_exceptions=False
        )
        assert result.exit_code == 0
        assert "main.tf" in result.output
        assert "bentoctl.tfvars" in result.output

    # init with no --do-not-generate flag
    with runner.isolated_filesystem():
        result = runner.invoke(
            bentoctl_cli,
            ["init", "--do-not-generate"],
            input="\n",
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "main.tf" not in result.output
        assert "bentoctl.tfvars" not in result.output

    result = runner.invoke(
        bentoctl_cli,
        ["init", "--save-path", str(tmp_path)],
        input="\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert str(tmp_path) in result.output


def test_cli_generate(monkeypatch):
    monkeypatch.setattr(bentoctl.cli, "DeploymentConfig", DeploymentConfigMock)
    runner = CliRunner()
    result = runner.invoke(bentoctl_cli, ["generate"])
    assert result.exit_code == 0
    assert "- main.tf" in result.output
    assert "- bentoctl.tfvars" in result.output


def test_cli_build(monkeypatch):
    monkeypatch.setattr(bentoctl.cli, "DeploymentConfig", DeploymentConfigMock)
    monkeypatch.setattr(
        bentoctl.cli, "build_docker_image", lambda **kwargs: print(kwargs)
    )
    monkeypatch.setattr(
        bentoctl.cli, "push_docker_image_to_repository", lambda **kwargs: print(kwargs)
    )
    monkeypatch.setattr(
        bentoctl.cli, "tag_docker_image", lambda *args: print(args)
    )

    runner = CliRunner()
    result = runner.invoke(
        bentoctl_cli,
        [
            "build",
            "--bento-tag",
            "testbento:latest",
            "--deployment_config_file",
            "deployment_config.yaml",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "generated template files" in result.output
    assert "- bentoctl.tfvars" in result.output
    assert "- main.tf" not in result.output

    # test dry run
    result = runner.invoke(
        bentoctl_cli,
        [
            "build",
            "--bento-tag",
            "testbento:latest",
            "--deployment_config_file",
            "deployment_config.yaml",
            "--dry-run"
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "generated template files" not in result.output
    assert "- bentoctl.tfvars" not in result.output
    assert "- main.tf" not in result.output
    assert "Created docker image:" in result.output
