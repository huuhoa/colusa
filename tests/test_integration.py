import unittest

from colusa import Colusa
from colusa.utils import get_short_hexdigest, get_hexdigest
import pathlib
import os
from unittest.mock import patch
import os.path


def download_image_mocked(url_path, *args, **kwargs):
    import urllib
    print(f'call download_image with {url_path}')
    result = urllib.parse.urlsplit(url_path)
    p = pathlib.PurePath(result.path)
    image_name = f'{get_hexdigest(url_path)}{p.suffix}'
    return image_name


def download_content_mocked(url_path: str):
    print(f'call colusa.Colusa.download_content with path {url_path}')
    cached_file_path = os.path.join('tests-cached', f'{get_hexdigest(url_path)}.html')
    with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
        content = file_in.read()
    return content


class ColusaIntegrationTestCase(unittest.TestCase):

    @patch('os.path.exists')
    def test_patch_exists(self, mock_os_path_exists):
        def side_effect(path: str):
            print(f'call os.path.exists with {path}')
            return path.startswith('tests-dist/images/')

        mock_os_path_exists.side_effect = side_effect

        self.assertTrue(os.path.exists('tests-dist/images/abc.png'))
        self.assertFalse(os.path.exists('tests-dist/.cached/images/abc.png'))

    @patch('colusa.Colusa.download_content')
    def test_mock_download_content(self, mock_download_content):
        def side_effect(url_path: str):
            print(f'call colusa.Colusa.download_content with path {url_path}')
            cached_file_path = os.path.join('tests-cached', f'{get_hexdigest(url_path)}.html')
            with open(cached_file_path, 'rt', encoding='utf-8') as file_in:
                content = file_in.read()
            return content

        mock_download_content.side_effect = side_effect

        configs = {
            "title": "test: test case",
            "author": "tester",
            "version": "v1.0",
            "homepage": "dummy",
            "output_dir": "tests-dist",
            "multi_part": False,
            "parts": [],
            "urls": [
                "https://staffeng.com/guides/overview-overview",
            ]
        }
        runner = Colusa(configs)
        runner.generate()
        mock_download_content.assert_called_once_with("https://staffeng.com/guides/overview-overview")

    @patch('colusa.Colusa.download_content')
    @patch('colusa.fetch.download_image')
    def test_whole_program(self, mock_download_image, mock_download_content):
        urls = [
            "https://staffeng.com/guides/overview-overview",
            "https://tech.trivago.com/2016/03/24/team-work-made-simple-with-guilds/",
            "https://techblog.constantcontact.com/software-development/tackling-tech-debt-frontend-guild/",
            "https://medium.com/@shawnstafford/ops-runbook-16017fa78733",
            "https://martinfowler.com/articles/patterns-legacy-displacement/",
            "https://doordash.engineering/2021/03/04/building-a-declarative-real-time-feature-engineering-framework/",
        ]

        """
        Mocking os.path.exists with using side_effect
        """
        mock_download_image.side_effect = download_image_mocked
        mock_download_content.side_effect = download_content_mocked

        for url in urls:
            configs = {
                "title": "test: test case",
                "author": "tester",
                "version": "v1.0",
                "homepage": "dummy",
                "output_dir": "tests-dist",
                "multi_part": False,
                "parts": [],
                "urls": [
                    url
                ]
            }
            runner = Colusa(configs)
            runner.generate()

            p = pathlib.PurePath(url)
            output_name = f'{p.name}_{get_short_hexdigest(url)}.asciidoc'
            self.assertTrue(self.compare_file(os.path.join('tests-dist', output_name),
                                              os.path.join('tests-expected', output_name)),
                            f'failed for url: {url}')

    def compare_file(self, actual_file, expected_file):
        import filecmp
        return filecmp.cmp(actual_file, expected_file)


if __name__ == '__main__':
    unittest.main()
