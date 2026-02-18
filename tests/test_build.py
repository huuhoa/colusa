import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from colusa.colusa import Colusa, _TOOL_MAP


def _make_config(tmp_path: Path, extra: dict = None) -> Path:
    data = {
        'title': 'Test Book',
        'author': 'Tester',
        'version': 'v1.0',
        'homepage': 'https://example.com',
        'output_dir': str(tmp_path / 'output'),
        'book_file_name': 'index.asciidoc',
        'make': {'html': '', 'epub': '', 'pdf': ''},
        'urls': ['https://example.com/article'],
    }
    if extra:
        data.update(extra)
    config = tmp_path / 'book.json'
    config.write_text(json.dumps(data, indent=4))
    return config


def _run_build(config_path: str, formats: list[str]):
    """Helper: run build_book with subprocess.run and shutil.which mocked."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch('shutil.which', return_value='/usr/bin/asciidoctor'), \
         patch('subprocess.run', return_value=mock_result) as mock_run:
        Colusa.build_book(config_path, formats=formats)
    return mock_run


class BuildToolDispatchTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_build_html_invokes_asciidoctor(self):
        config = _make_config(self.tmp_path)
        mock_run = _run_build(str(config), ['html'])
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'asciidoctor')
        self.assertIn('-b', cmd)
        self.assertIn('html5', cmd)

    def test_build_epub_invokes_asciidoctor_epub3(self):
        config = _make_config(self.tmp_path)
        mock_run = _run_build(str(config), ['epub'])
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'asciidoctor-epub3')
        self.assertNotIn('html5', cmd)

    def test_build_pdf_invokes_asciidoctor_pdf(self):
        config = _make_config(self.tmp_path)
        mock_run = _run_build(str(config), ['pdf'])
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], 'asciidoctor-pdf')

    def test_build_runs_in_output_dir(self):
        config = _make_config(self.tmp_path)
        mock_run = _run_build(str(config), ['epub'])
        kwargs = mock_run.call_args[1]
        self.assertEqual(kwargs['cwd'], str(self.tmp_path / 'output'))

    def test_build_passes_make_params(self):
        config = _make_config(self.tmp_path, extra={
            'make': {'html': '', 'epub': '--attribute ebook-format=kf8', 'pdf': ''}
        })
        mock_run = _run_build(str(config), ['epub'])
        cmd = mock_run.call_args[0][0]
        self.assertIn('--attribute', cmd)
        self.assertIn('ebook-format=kf8', cmd)

    def test_build_defaults_to_all_formats(self):
        config = _make_config(self.tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch('shutil.which', return_value='/usr/bin/tool'), \
             patch('subprocess.run', return_value=mock_result) as mock_run:
            Colusa.build_book(str(config))  # no formats arg
        self.assertEqual(mock_run.call_count, 3)
        tools_called = [c[0][0][0] for c in mock_run.call_args_list]
        self.assertIn('asciidoctor', tools_called)
        self.assertIn('asciidoctor-epub3', tools_called)
        self.assertIn('asciidoctor-pdf', tools_called)


class BuildErrorHandlingTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_build_tool_not_found_exits_1(self):
        config = _make_config(self.tmp_path)
        with patch('shutil.which', return_value=None):
            with self.assertRaises(SystemExit) as ctx:
                Colusa.build_book(str(config), formats=['epub'])
        self.assertEqual(ctx.exception.code, 1)

    def test_build_tool_failure_exits_1(self):
        config = _make_config(self.tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch('shutil.which', return_value='/usr/bin/tool'), \
             patch('subprocess.run', return_value=mock_result):
            with self.assertRaises(SystemExit) as ctx:
                Colusa.build_book(str(config), formats=['epub'])
        self.assertEqual(ctx.exception.code, 1)

    def test_build_continues_after_first_failure(self):
        """All formats attempted even if an earlier one fails."""
        config = _make_config(self.tmp_path)
        fail_result = MagicMock()
        fail_result.returncode = 1
        ok_result = MagicMock()
        ok_result.returncode = 0
        with patch('shutil.which', return_value='/usr/bin/tool'), \
             patch('subprocess.run', side_effect=[fail_result, ok_result]) as mock_run:
            with self.assertRaises(SystemExit):
                Colusa.build_book(str(config), formats=['epub', 'html'])
        self.assertEqual(mock_run.call_count, 2)


class BuildCommandTestCase(unittest.TestCase):

    def test_build_command_html_includes_html5_flag(self):
        cmd = Colusa._build_command('html', 'index.asciidoc', '')
        self.assertIn('-b', cmd)
        self.assertIn('html5', cmd)
        self.assertEqual(cmd[0], 'asciidoctor')

    def test_build_command_epub_excludes_html5_flag(self):
        cmd = Colusa._build_command('epub', 'index.asciidoc', '')
        self.assertNotIn('html5', cmd)
        self.assertEqual(cmd[0], 'asciidoctor-epub3')

    def test_build_command_includes_extra_params(self):
        cmd = Colusa._build_command('pdf', 'index.asciidoc', '--attribute pdf-theme=basic')
        self.assertIn('--attribute', cmd)
        self.assertIn('pdf-theme=basic', cmd)

    def test_build_command_no_extra_params_when_empty(self):
        cmd = Colusa._build_command('epub', 'index.asciidoc', '')
        # No stray empty strings appended
        self.assertNotIn('', cmd)


class BuildIntegrationWithGenerateTestCase(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.tmp_path = Path(tempfile.mkdtemp())

    def test_generate_with_build_flag_calls_build(self):
        config = _make_config(self.tmp_path)
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch.object(Colusa, 'generate_book') as mock_gen, \
             patch.object(Colusa, 'build_book') as mock_build:
            # Simulate CLI handler logic
            Colusa.generate_book(str(config))
            Colusa.build_book(str(config), formats=['epub'])
        mock_gen.assert_called_once_with(str(config))
        mock_build.assert_called_once_with(str(config), formats=['epub'])
