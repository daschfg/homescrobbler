from setuptools import setup, find_packages
from homescrobbler import __progname__, __version__

setup(
    name=__progname__,
    version=__version__,
    license='GPLv3+',
    packages=find_packages()
)
