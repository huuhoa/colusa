# !/usr/bin/env python3
from setuptools import setup, find_packages
import io
import os


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names), encoding=kwargs.get('encoding', 'utf8')
    ) as fin:
        return fin.read()


requirements = []
with open('requirements.txt') as fh:
    for line in fh.readlines():
        requirements.append(line.strip())

pkg_info = {}
version_info = read('src/colusa/_version.py')
exec(version_info, pkg_info)

NEW_LINE = '\n'
PACKAGE_NAME = 'colusa'

setup(name=PACKAGE_NAME,
      url='http://github.com/huuhoa/colusa',
      version=pkg_info['__version__'],
      description=pkg_info['__description__'],
      long_description=f"{read('README.md')}{NEW_LINE}{read('CHANGELOG.md')}",
      long_description_content_type="text/markdown",
      author=pkg_info['__author__'],
      author_email=pkg_info['__email__'],
      maintainer=pkg_info['__author__'],
      maintainer_email=pkg_info['__email__'],
      license=pkg_info['__license__'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
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
