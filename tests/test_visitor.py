import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from colusa.visitor import NodeVisitor


class CommentNodeTestCase(unittest.TestCase):
    """HTML Comment nodes must be silently dropped with no warning."""

    def _visit(self, html: str) -> str:
        bs = BeautifulSoup(html, 'html.parser')
        return NodeVisitor().visit(bs)

    def test_comment_produces_no_output(self):
        result = self._visit('<div><!-- this is a comment -->hello</div>')
        self.assertNotIn('this is a comment', result)
        self.assertIn('hello', result)

    def test_comment_does_not_log_warning(self):
        with patch('colusa.visitor.logs.warn') as mock_warn:
            self._visit('text<!-- comment -->more')
        # No "UNKNOWN Node Type" warning should be produced for Comment nodes
        for call in mock_warn.call_args_list:
            self.assertNotIn('UNKNOWN Node Type', str(call))

    def test_multiple_comments_are_all_dropped(self):
        result = self._visit('<!-- a -->hello<!-- b --> world<!-- c -->')
        self.assertNotIn('a', result)
        self.assertNotIn('b', result)
        self.assertNotIn('c', result)
        self.assertIn('hello', result)
        self.assertIn('world', result)

    def test_plain_text_nodes_still_rendered(self):
        result = self._visit('<p>plain text</p>')
        self.assertIn('plain text', result)

    def test_comment_only_document_produces_empty_output(self):
        result = self._visit('<!-- only a comment -->')
        self.assertEqual(result.strip(), '')
