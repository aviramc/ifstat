from setuptools import setup, find_packages
import os.path

def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path, "rb") as fp:
        return fp.read()

VERSION = "1.0.0"

setup(
    name = "ifstat",
    version = VERSION,
    author = "Aviram Cohen",
    # author_email = "aviramc@gmail.com",
    description = "Display and retrieve network interface statistics",
    license = "Apache 2.0",
    keywords = "network statistics",
    url = "https://github.com/aviramc/ifstat",
    packages = find_packages(),
    long_description = read('README.md'),
    install_requires = [
        # "requests == 2.6.0",
    ],
    include_package_data = True,
    entry_points = dict(
        console_scripts = [
            "ifstat = ifstat.ifstat:main",
        ]
    ),
    zip_safe = False
)
