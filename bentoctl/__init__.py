try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

# Find bentoctl version managed by pyproject.toml
__version__: str = importlib_metadata.version("bentoctl")
