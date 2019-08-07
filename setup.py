from setuptools import setup, find_packages

setup(
    name='collaborative_platform',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    version='0.1.0',
)
