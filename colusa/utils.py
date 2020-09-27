import hashlib
import os
import pathlib
import shutil

import requests
from idna import unicode
import unicodedata
import re

from colusa import logs


def download_url(url_path: str, file_path: str):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'curl/7.64.1',
    }
    req = requests.get(url_path, headers=headers, stream=True)
    if req.status_code != 200:
        logs.error(f'Cannot make request. Result: {req.status_code:d}')
        exit(1)

    with open(file_path, 'wb') as file_out:
        req.raw.decode_content = True
        shutil.copyfileobj(req.raw, file_out)


def get_hexdigest(str_value: str) -> str:
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()


def download_image(url_path, output_dir):
    p = pathlib.PurePath(url_path)
    image_name = f'{get_hexdigest(url_path)}{p.suffix}'
    image_path = os.path.join(output_dir, "images", image_name)
    if not os.path.exists(image_path):
        download_url(url_path, image_path)
    return image_name


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    Copied from: https://gist.github.com/berlotto/6295018
    """

    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


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
