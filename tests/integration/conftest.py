import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--url",
        action="store",
        default="http://localhost:3000",
        help="URL for the endpoint that is hosted",
    )
    parser.addoption(
        "--target",
        action="store",
        default="default",
        help="based on the target specified, some tests will be skiped. Valid"
        "options: [default, sagemaker]",
    )


@pytest.fixture
def url(request):
    return request.config.getoption("--url")


@pytest.fixture()
def target(request):
    return request.config.getoption("--target")
