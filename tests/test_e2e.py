import os
import sys
import io
import unittest
import logging
from contextlib import redirect_stdout

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from simulator import main


class TestE2E(unittest.TestCase):

    def test_all_yaml_files(self):
        yaml_dir = os.path.join(os.path.dirname(__file__), 'yaml')
        for filename in os.listdir(yaml_dir):
            if filename.endswith('.yaml'):
                with self.subTest(filename=filename):
                    self.run_test_for_file(os.path.join(yaml_dir, filename))

    def run_test_for_file(self, yaml_file):
        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            main(yaml_file, log_level=logging.ERROR)  # Use ERROR level to minimize output in tests

        output = captured_output.getvalue()

        # Load expected output
        expected_output_file = yaml_file.replace('.yaml', '_expected.txt')
        with open(expected_output_file, 'r') as f:
            expected_output = f.read()

        # Compare output
        self.assertEqual(output.strip(), expected_output.strip())


if __name__ == '__main__':
    unittest.main()
