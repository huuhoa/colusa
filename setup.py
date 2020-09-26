# !/usr/bin/env python3

from setuptools import setup

setup(name='colusa',
      version='0.3.0',
      description='Render website to ebook to make it easier to read on devices',
      url='http://github.com/huuhoa/colusa',
      author='Huu Hoa NGUYEN',
      author_email='huuhoa@gmail.com',
      license='MIT',
      packages=['colusa'],
      install_requires=[
          'beautifulsoup4==4.9.1',
          'certifi==2020.6.20',
          'chardet==3.0.4',
          'idna==2.10',
          'requests==2.24.0',
          'soupsieve==2.0.1',
          'urllib3==1.25.10',
          'python-dateutil~=2.8.1'
      ],
      entry_points={
          'console_scripts': [
              'colusa = colusa.cli:main'
          ]
      })
