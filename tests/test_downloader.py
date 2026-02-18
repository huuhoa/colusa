import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests

from colusa import fetch


class DownloaderDownloadUrlTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.out_path = os.path.join(self.tmp_dir, 'page.html')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    @patch('colusa.fetch.Fetch.get')
    def test_non_200_writes_temp_file(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b'not found'
        mock_get.return_value = mock_resp

        with fetch.Downloader() as dl:
            dl.download_url('https://example.com/page', self.out_path)

        self.assertTrue(os.path.exists(self.out_path + '.temp'))
        self.assertFalse(os.path.exists(self.out_path))

    @patch('colusa.fetch.Fetch.get')
    def test_non_200_temp_file_contains_response_body(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.content = b'server error body'
        mock_get.return_value = mock_resp

        with fetch.Downloader() as dl:
            dl.download_url('https://example.com/page', self.out_path)

        with open(self.out_path + '.temp', 'rb') as f:
            self.assertEqual(f.read(), b'server error body')

    @patch('colusa.fetch.shutil.copyfileobj')
    @patch('colusa.fetch.Fetch.get')
    def test_200_calls_copyfileobj_to_write_output(self, mock_get, mock_copy):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        with fetch.Downloader() as dl:
            dl.download_url('https://example.com/page', self.out_path)

        mock_copy.assert_called_once()

    @patch('colusa.fetch.Fetch.get')
    def test_200_sets_decode_content_on_raw(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        with patch('colusa.fetch.shutil.copyfileobj'):
            with fetch.Downloader() as dl:
                dl.download_url('https://example.com/page', self.out_path)

        self.assertTrue(mock_resp.raw.decode_content)


class DownloadImageTestCase(unittest.TestCase):

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_connection_error_does_not_propagate(self, _exists, mock_dl):
        mock_dl.side_effect = requests.exceptions.ConnectionError('refused')
        fetch.download_image('https://example.com/img.png', '/tmp')  # must not raise

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_request_exception_does_not_propagate(self, _exists, mock_dl):
        mock_dl.side_effect = requests.exceptions.Timeout('timed out')
        fetch.download_image('https://example.com/img.png', '/tmp')  # must not raise

    @patch('os.path.exists', return_value=True)
    def test_cached_image_skips_download(self, _exists):
        with patch.object(fetch.Downloader, 'download_url') as mock_dl:
            fetch.download_image('https://example.com/img.png', '/tmp')
            mock_dl.assert_not_called()

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_returns_filename_with_correct_extension(self, _exists, _dl):
        name = fetch.download_image('https://example.com/photo.jpg', '/tmp')
        self.assertTrue(name.endswith('.jpg'))

    @patch('colusa.fetch.Downloader.download_url')
    @patch('os.path.exists', return_value=False)
    def test_returns_filename_with_no_extension_for_extensionless_url(self, _exists, _dl):
        name = fetch.download_image('https://example.com/image', '/tmp')
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
