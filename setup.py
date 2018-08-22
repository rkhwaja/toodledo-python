#!/usr/bin/env python3

"""Pretty standard setup.py"""

from setuptools import find_packages, setup

with open("README.rst") as f:
	long_description = f.read()

setup(name="toodledo",
	version="0.7",
	description="Python wrapper for the Toodledo v3 API which is documented at http://api.toodledo.com/3/",
	long_description=long_description,
	author="Rehan Khwaja",
	author_email="rehan@khwaja.name",
	url="https://github.com/rkhwaja/toodledo-python",
	packages=find_packages(),
	install_requires=["marshmallow", "requests", "requests_oauthlib"],
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7"
	],
	keywords="",
)
