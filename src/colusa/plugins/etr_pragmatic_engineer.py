from colusa.etr import Extractor, Transformer, register_extractor_v2, register_transformer_v2
from colusa.asciidoc_visitor import AsciidocVisitor
from bs4 import Tag
import re
from colusa import logs
import requests
import json


@register_extractor_v2('substack', '//newsletter.pragmaticengineer.com|learnings.aleixmorgadas.dev')
class PragmaticEngineerExtractor(Extractor):
    def cleanup(self):
        self.remove_tag(self.main_content, 'div', attrs={'class': 'subscribe-widget'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'share-dialog'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-footer'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'subscribe-footer'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'publication-footer'})
        self.remove_tag(self.main_content, 'a', attrs={'class': 'post-ufi-button'})
        self.remove_tag(self.main_content, 'a', attrs={'class': 'tweet-link-bottom'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'tweet-header'})
        self.remove_tag(self.main_content, 'ul', attrs={'class': 'subscribe-prompt-dropdown'})
        self.remove_tag(self.main_content, 'h1', attrs={'class': 'post-title'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'post-label'})
        self.remove_tag(self.main_content, 'div', attrs={'class': 'profile-hover-card-target'})
        self.remove_tag(self.main_content, 'p', attrs={'class': 'button-wrapper'})

        super(PragmaticEngineerExtractor, self).cleanup()


class PEAsciidocVisitor(AsciidocVisitor):
    visit_tag_source = AsciidocVisitor.visit_tag_fall_through
    # visit_tag_div = AsciidocVisitor.visit_tag_fall_through

    def visit_tag_a(self, node, *args, **kwargs):
        href = node.get('href', '')
        # kwargs['href'] = href
        text = self.generic_visit(node, *args, **kwargs)
        # del kwargs['href']
        if not text:
            return ''
        m = re.match(r'https?://', href)
        if m is None:
            return text
        # special handling for tweet
        class_ = node.get('class', [])
        if 'tweet-link-top' in class_:
            # render as pre
            return f'''[listing]
....
{text}
....

'''
        img = node.find('figure')
        if img:
            return self.visit_tag_figure(img, *args, **kwargs)

        img = node.find('img')
        if img:
            return self.visit_tag_img(img, *args, **kwargs)

        if kwargs.get('figure', False):
            # parent is figure, no need to create a link
            return text

        return f'link:{href}[{text}]'
    
    def visit_tag_figure(self, node, *args, **kwargs):
        kwargs['figure'] = True
        text = super().visit_tag_figure(node, *args, **kwargs)
        del kwargs['figure']
        return text
    
    def visit_tag_blockquote(self, node, *args, **kwargs):
        kwargs['blockquote'] = True
        text = super().visit_tag_blockquote(node, *args, **kwargs)
        del kwargs['blockquote']
        return text

    def visit_heading_node(level):
        def visitor(self, node, *args, **kwargs):
            text = self.generic_visit(node, *args, **kwargs)
            text = self.text_cleanup(text)
            if not text:
                # empty heading
                return '\n\n'
            
            class_ = node.get('class', [])
            if 'subtitle' in class_:
                return f'\n{text}\n\n'

            if kwargs.get('blockquote', False):
                # skip heading
                return f'\n{text}\n\n'
            else:
                return f'\n{"=" * level} {text}\n\n'

        return visitor

    visit_tag_h1 = visit_heading_node(2)
    visit_tag_h2 = visit_heading_node(2)
    visit_tag_h3 = visit_heading_node(3)
    visit_tag_h4 = visit_heading_node(4)


@register_transformer_v2('substack', '//newsletter.pragmaticengineer.com|learnings.aleixmorgadas.dev')
class PragmaticEngineerTransformer(Transformer):
    def create_visitor(self):
        return PEAsciidocVisitor()


import json
from colusa.fetch import Fetch, register_fetch

class SubstackAPIException(Exception):
    def __init__(self, status_code, text):
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = f"Invalid JSON error message from Substack: {text}"
        else:
            self.message = ", ".join(
                list(
                    map(lambda error: error.get("msg", ""), json_res.get("errors", []))
                )
            )
            self.message = self.message or json_res.get("error", "")
        self.status_code = status_code

    def __str__(self):
        return f"APIError(code={self.status_code}): {self.message}"


class SubstackRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"SubstackRequestException: {self.message}"


class SectionNotExistsException(SubstackRequestException):
    pass

@register_fetch('pragmaticengineer', r'https://newsletter.pragmaticengineer.com/.*')
class SubstackFetch(Fetch):
    """

    A python interface into the Substack API

    """

    def __init__(
        self,
        config: dict,
    ):
        """

        To create an instance of the substack.Api class:
            >>> import substack
            >>> api = substack.SubstackFetch({'email': "substack email", 'password': "substack password"})

        Args:
          email:
          password:
          cookies_path
            To re-use your session without logging in each time, you can save your cookies to a json file and
            then load them in the next session.
            Make sure to re-save your cookies, as they do update over time.
          base_url:
            The base URL to use to contact the Substack API.
            Defaults to https://substack.com/api/v1.
        """
        super().__init__(config)
        email=self.config.get('email')
        password=self.config.get('password')
        cookies_path=self.config.get('cookies_path')
        base_url=self.config.get('base_url')
        self.match_url=self.config.get('match_url', r'https://newsletter.pragmaticengineer.com/.*')
        self.base_url = base_url or "https://substack.com/api/v1"
        renew_cookie = self.config.get('renew_cookie', False)
        self.persist_cookie = self.config.get('persist_cookie', False)
        self._session = requests.Session()

        # Load cookies from file if provided
        # Helps with Captcha errors by reusing cookies from "local" auth, then switching to running code in the cloud
        if not renew_cookie and cookies_path is not None:
            with open(cookies_path) as f:
                cookies = json.load(f)
            self._session.cookies.update(cookies)

        elif email is not None and password is not None:
            self.login(email, password)
        else:
            raise ValueError(
                "Must provide email and password or cookies_path to authenticate."
            )

    def can_process(self, url: str):
        if re.match(self.match_url, url):
            return True
        else:
            return False

    def close(self):
        """
        Close the _session and other resources
        """
        if self.persist_cookie:
            self.export_cookies()
        self._session.close()

    def login(self, email, password) -> dict:
        """

        Login to the substack account.

        Args:
          email: substack account email
          password: substack account password
        """

        response = self._session.post(
            f"{self.base_url}/email-login",
            json={
                "captcha_response": None,
                "email": email,
                "for_pub": "",
                "password": password,
                "redirect": "/",
            },
        )

        return SubstackFetch._handle_response(response=response)


    def export_cookies(self, path: str = "cookies.json"):
        """
        Export cookies to a json file.
        Args:
            path: path to the json file
        """
        cookies = self._session.cookies.get_dict()
        with open(path, "w") as f:
            json.dump(cookies, f, indent=3)

    @staticmethod
    def _handle_response(response: requests.Response):
        """

        Internal helper for handling API responses from the Substack server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.

        """

        if not (200 <= response.status_code < 300):
            raise SubstackAPIException(response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise SubstackRequestException("Invalid Response: %s" % response.text)

    def request(self, method, url, **kwargs):
        # logs.info(f'calling PE fetch: method: {method}, url: {url}')
        # print(self._session.cookies.items())
        return self._session.request(method=method, url=url, **kwargs)
