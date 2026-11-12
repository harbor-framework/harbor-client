"""Attach typing metadata to the otherwise generated setuptools package."""
from setuptools import setup
from build_support import TypedBuildPy

setup(cmdclass={"build_py": TypedBuildPy})
