from setuptools import setup

install_requires = [
    "click>7.0",
    "cerberus",
    "bentoml",
    "rich",
    "simple-term-menu",
    "cloup",
    "PyYAML",
    "GitPython",
]

dev_requires = [
    "flake8>=3.8.2",
    "pylint>=2.6.2",
    "pytest",
    "coverage>=4.4",
    "pytest-cov>=2.7.1",
]

dev_all = install_requires + dev_requires

extras_require = {
    "dev": dev_all,
}

setup(
    name="bentoctl",
    version="0.1.0",
    py_modules=["cli"],
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={"console_scripts": ["bentoctl = bentoctl.cli:bentoctl"]},
)
