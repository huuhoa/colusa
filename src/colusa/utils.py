import hashlib
import os
import pathlib
import shutil

import requests
import re

from colusa import logs

def get_hexdigest(str_value: str) -> str:
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()


def get_short_hexdigest(str_value: str) -> str:
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()[:8]



def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.

    From Django's "django/template/defaultfilters.py".
    Copied from: https://github.com/django/django/blob/a6b3938afc0204093b5356ade2be30b461a698c5/django/utils/text.py#L394

    """

    import unicodedata

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
    return re.sub(r'[-\s]+', '-', value)


def scan(namespace):
    """ Scans the namespace for modules and imports them, to activate decorator
    """

    import importlib
    import pkgutil

    name = importlib.util.resolve_name(namespace, package=__package__)
    spec = importlib.util.find_spec(name)

    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
            spec = finder.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

