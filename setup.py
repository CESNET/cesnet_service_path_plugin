import codecs
import os.path

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_config_param(rel_path, variable_name):
    for line in read(rel_path).splitlines():
        if line.startswith(variable_name):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError(f"Unable to find {variable_name} string.")


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name=get_config_param("komora_service_path_plugin/version.py", "__name__"),
    version=get_version("komora_service_path_plugin/version.py"),
    description=get_config_param(
        "komora_service_path_plugin/version.py", "__description__"
    ),
    author=get_config_param("komora_service_path_plugin/version.py", "__author__"),
    license="MIT",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
