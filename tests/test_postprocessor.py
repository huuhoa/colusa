import unittest

from colusa import etr


class PostProcessorBaseTestCase(unittest.TestCase):

    def test_run_is_noop(self):
        pp = etr.PostProcessor('/some/file.asciidoc', [])
        pp.run()  # must not raise

    def test_stores_file_path(self):
        pp = etr.PostProcessor('/output/chapter.asciidoc', [])
        self.assertEqual(pp.file_path, '/output/chapter.asciidoc')

    def test_stores_params(self):
        pp = etr.PostProcessor('/output/chapter.asciidoc', ['a', 'b'])
        self.assertEqual(pp.params, ['a', 'b'])

    def test_empty_params_stored_as_empty_list(self):
        pp = etr.PostProcessor('/output/chapter.asciidoc', [])
        self.assertEqual(pp.params, [])


class CreatePostProcessorTestCase(unittest.TestCase):

    def test_raises_for_unknown_name(self):
        with self.assertRaises(etr.PostProcessorNotFoundError):
            etr.create_postprocessor('no-such-processor', '/tmp/f.asciidoc', [])

    def test_error_contains_processor_name(self):
        with self.assertRaises(etr.PostProcessorNotFoundError) as ctx:
            etr.create_postprocessor('my-missing-proc', '/tmp/f.asciidoc', [])
        self.assertIn('my-missing-proc', str(ctx.exception))

    def test_error_message_format(self):
        err = etr.PostProcessorNotFoundError('my-proc')
        self.assertEqual(str(err), 'Post Processor my-proc is not registered')

    def test_registered_processor_is_instantiated(self):
        @etr.register_postprocessor('_test_proc_instantiate')
        class _TestProc(etr.PostProcessor):
            pass

        pp = etr.create_postprocessor('_test_proc_instantiate', '/tmp/f.asciidoc', ['x'])
        self.assertEqual(type(pp).__name__, '_TestProc')
        self.assertEqual(pp.file_path, '/tmp/f.asciidoc')
        self.assertEqual(pp.params, ['x'])
