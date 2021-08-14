import hashlib
import os
import pathlib
import shutil

import requests
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


def get_short_hexdigest(str_value: str) -> str:
    m = hashlib.sha256()
    m.update(str_value.encode('utf-8'))
    return m.hexdigest()[:8]


def download_image(url_path, output_dir):
    import urllib

    result = urllib.parse.urlsplit(url_path)
    p = pathlib.PurePath(result.path)
    image_name = f'{get_hexdigest(url_path)}{p.suffix}'
    image_path = os.path.join(output_dir, "images", image_name)
    if not os.path.exists(image_path):
        try:
            download_url(url_path, image_path)
        except requests.exceptions.ConnectionError as ex:
            logs.warn(f'error while downloading image. Exception: {ex}')
        
    return image_name


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
