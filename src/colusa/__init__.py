# -*- coding: utf-8 -*-
"""Top-level package for colusa.

Copyright (c) 2020-2024 Huu Hoa NGUYEN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from colusa import _version

__author__ = _version.__author__
__email__ = _version.__email__
__version__ = _version.__version__
__copyright__ = _version.__copyright__
__license__ = _version.__license__

__all__ = ['Colusa', 'ConfigurationError', 'logs', 'Crawler']


from colusa import logs
from .crawlers import Crawler as Crawler
from colusa import etr as etr
from colusa.exceptions import ConfigurationError as ConfigurationError
from colusa import utils as utils
from colusa.colusa import Colusa as Colusa
