import hashlib
import os
import pathlib
import shutil
import re
from typing import Any, Optional

import requests

from colusa import logs


def get_hexdigest(str_value: str) -> str:
    """Calculate SHA-256 hex digest of the given string.
    
    Args:
        str_value: Input string to hash
        
    Returns:
        Full SHA-256 hex digest string
    """
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()


def get_short_hexdigest(str_value: str) -> str:
    """Calculate truncated SHA-256 hex digest of the given string.
    
    Args:
        str_value: Input string to hash
        
    Returns:
        First 8 characters of SHA-256 hex digest
    """
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()[:8]


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.

    From Django's "django/template/defaultfilters.py".
    Copied from: https://github.com/django/django/blob/a6b3938afc0204093b5356ade2be30b461a698c5/django/utils/text.py#L394

    Args:
        value: String to slugify
        allow_unicode: Whether to allow unicode characters
        
    Returns:
        Slugified string
    """
    import unicodedata

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
    return re.sub(r'[-\s]+', '-', value)


def scan(namespace: str) -> None:
    """Scans the namespace for modules and imports them, to activate decorator.
    
    Args:
        namespace: The Python namespace to scan (e.g., 'colusa.plugins')
    """
    import importlib
    import importlib.util
    import pkgutil

    name = importlib.util.resolve_name(namespace, package=__package__)
    spec = importlib.util.find_spec(name)

    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)

        if module.__path__ is not None:
            for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
                spec = finder.find_spec(name)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    if spec.loader is not None:
                        spec.loader.exec_module(module)
