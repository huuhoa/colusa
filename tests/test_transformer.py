import unittest

from colusa.etr import Transformer
from bs4 import BeautifulSoup


def read_file(file_path):
    with open(file_path) as file_in:
        data = file_in.read()

    return data


class TransformerTestCase(unittest.TestCase):
    def test_tag_p_1(self):
        test_data = read_file('tests/data/p_1.html')
        expected_output = read_file('tests/data/p_1.txt')
        bs = BeautifulSoup(test_data, 'html.parser')
        sp = Transformer({
            'src_url': 'https://dummy',
            'output_dir': 'temp'
        }, bs)
        actual_data = sp.transform()

        self.assertEqual(expected_output, actual_data)


if __name__ == '__main__':
    unittest.main()
