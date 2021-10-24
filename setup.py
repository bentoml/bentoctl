from setuptools import setup

setup(
    name="bcdt",
    version="0.1.0",
    py_modules=["cli"],
    install_requires=["Click", "cerberus", "bentoml", "rich", "simple-term-menu"],
    entry_points={
        "console_scripts": [
            "bcdt = bcdt.cli:bcdt",
        ],
    },
)
