# !/usr/bin/env python3
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='colusa',
      version='0.6.0',
      description='Render website to ebook to make it easier to read on devices',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/huuhoa/colusa',
      author='Huu Hoa NGUYEN',
      author_email='huuhoa@gmail.com',
      license="MIT License",
      packages=['colusa'],
      install_requires=[
            'beautifulsoup4>=4.9',
            'certifi==2021.5.30',
            'chardet==4.0.0',
            'idna==3.2',
            'requests==2.26.0',
            'soupsieve==2.2.1',
            'urllib3>=1.25',
            'python-dateutil~=2.8.1',
            'PyYAML==5.4.1',
            'torpy~=1.1.4',
            'setuptools==57.4.0',
      ],
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
