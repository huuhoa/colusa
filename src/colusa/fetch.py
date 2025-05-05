import hashlib
import os
import pathlib
import shutil

import requests
import re

from colusa import logs, utils

_FETCH_MAP = {
}

class Fetch:
    def __init__(self, config={}) -> None:
        self.config = config

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
    
    def can_process(self, url: str):
        """
        Determine if can handle given URL or not
        """
        return True

    def request(self, method, url, **kwargs):
        """Constructs and sends a :class:`Request <Request>`.

        :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
            ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
            or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
            defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
            to add for the file.
        :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How many seconds to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
                the server's TLS certificate, or a string, in which case it must be a path
                to a CA bundle to use. Defaults to ``True``.
        :param stream: (optional) if ``False``, the response content will be immediately downloaded.
        :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response

        Usage::

        >>> import requests
        >>> req = requests.request('GET', 'https://httpbin.org/get')
        >>> req
        <Response [200]>
        """

        # By using the 'with' statement we are sure the session is closed, thus we
        # avoid leaving sockets open which can trigger a ResourceWarning in some
        # cases, and look like a memory leak in others.
        with requests.sessions.Session() as session:
            return session.request(method=method, url=url, **kwargs)


    def get(self, url, params=None, **kwargs):
        r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("get", url, params=params, **kwargs)

    def options(self, url, **kwargs):
        r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("options", url, **kwargs)

    def head(self, url, **kwargs):
        r"""Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes. If
            `allow_redirects` is not provided, it will be set to `False` (as
            opposed to the default :meth:`request` behavior).
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        kwargs.setdefault("allow_redirects", False)
        return self.request("head", url, **kwargs)


    def post(self, url, data=None, json=None, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("post", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("put", url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("patch", url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request("delete", url, **kwargs)

class Downloader():
    UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15'
    def __init__(self, downloader_config = {}) -> None:
        self.clients = []
        for key, config in downloader_config.items():
            pattern, fetcher_cls = _FETCH_MAP.get(key, (None, None))
            if pattern is None or fetcher_cls is None:
                continue
            self.clients.append((pattern, fetcher_cls(config)))

        self.clients.append((r'.*', Fetch({})))

    def close(self):
        for _, ins in self.clients:
            ins.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def get_fetch_instance(self, url_path: str) -> Fetch:
        for pattern, fetch_obj in self.clients:
            if fetch_obj.can_process(url_path):
                return fetch_obj
            # if re.match(pattern, url_path):
            #     return fetch_obj

    def download_url(self, url_path: str, file_path: str):
        headers = {
            'Accept': '*/*',
            'User-Agent': self.UserAgent,
        }
        fetch = self.get_fetch_instance(url_path)
        req = fetch.get(url_path, headers=headers, stream=True)
        if req.status_code != 200:
            logs.error(f'Cannot make request. Result: {req.status_code:d}. URL: {url_path}')
            with open(f'{file_path}.temp', 'wb') as file_out:
                file_out.write(req.content)
            return

        with open(file_path, 'wb') as file_out:
            req.raw.decode_content = True
            shutil.copyfileobj(req.raw, file_out)

def download_image(url_path, output_dir):
    import urllib

    # logs.info(f'call download_image with url_path is {url_path}')
    result = urllib.parse.urlsplit(url_path)
    p = pathlib.PurePath(result.path)
    image_name = f'{utils.get_hexdigest(url_path)}{p.suffix}'
    image_path = os.path.join(output_dir, "images", image_name)
    if not os.path.exists(image_path):
        try:
            with Downloader() as fetch:
                fetch.download_url(url_path, image_path)
        except requests.exceptions.ConnectionError as ex:
            logs.warn(f'error while downloading image. Exception: {ex}')
        except Exception as ex:
            logs.error(f'error with URL: {url_path}. Exception: {ex}')

    return image_name


_FETCH_MAP = {
}
def register_fetch(name: str, pattern: str):
    """Register url content fetcher class"""
    def decorator(cls):
        _FETCH_MAP[name] = (pattern, cls)
        return cls

    return decorator
