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
    "twine",
]

dev_all = install_requires + dev_requires

extras_require = {
    "dev": dev_all,
}


with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()

setup(
    name="bentoctl",
    version="0.1.1",
    py_modules=["cli"],
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={"console_scripts": ["bentoctl = bentoctl.cli:bentoctl"]},
    project_urls={
        "Source": "https://github.com/bentoml/bentoctl",
        "User Slack community": "https://bit.ly/2N5IpbB",
        "Bug Reports": "https://github.com/bentoml/bentoctl/issues",
    },
    python_requires=">=3.6.1",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
    ],
    description="Command line tool for deploying ML models to the cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bentoml/bentoctl",
    author="bentoml.org",
    author_email="contact@bentoml.ai",
)
