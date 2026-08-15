from setuptools import setup

# Package metadata lives in pyproject.toml. Keeping this shim import-free is
# important for PEP 517 editable builds, where the application package is not
# installed (or necessarily importable) when setuptools evaluates setup.py.
setup()
