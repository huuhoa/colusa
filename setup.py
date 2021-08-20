# !/usr/bin/env python3
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
with open('requirements.txt') as fh:
    for line in fh.readlines():
        requirements.append(line.strip())

pkg_info = {}
with open('colusa/_version.py') as fh:
    version_info = fh.read()
exec(version_info, pkg_info)

PACKAGE_NAME = 'colusa'

setup(name=PACKAGE_NAME,
      url='http://github.com/huuhoa/colusa',
      version=pkg_info['__version__'],
      description=pkg_info['__description__'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author=pkg_info['__author__'],
      author_email=pkg_info['__email__'],
      maintainer=pkg_info['__author__'],
      maintainer_email=pkg_info['__email__'],
      license=pkg_info['__license__'],
      packages=[PACKAGE_NAME],
      install_requires=requirements,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      entry_points={
          'console_scripts': [
              'colusa = colusa.cli:main'
          ]
      })
