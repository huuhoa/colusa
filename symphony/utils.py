import hashlib
import os
import pathlib
import shutil

import requests


def download_url(url_path: str, file_path: str):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'curl/7.64.1',
    }
    req = requests.get(url_path, headers=headers, stream=True)
    if req.status_code != 200:
        print(f'Cannot make request. Result: {req.status_code:d}')
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
