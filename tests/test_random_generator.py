# kendall-simulator/tests/test_random_generator.py
import unittest
from src.kendall_simulator.random_generator import (
    RandomNumberGenerator,
    linear_congruential_method,
)


class TestRandomNumberGenerator(unittest.TestCase):
    def test_predefined_numbers(self):
        numbers = [0.1, 0.2, 0.3, 0.4, 0.5]
        rng = RandomNumberGenerator(predefined_nums=numbers)
        self.assertEqual(rng.get_nums(), numbers)

    def test_generated_numbers(self):
        rng = RandomNumberGenerator(quantity=1000, seed=42)
        numbers = rng.get_nums()
        self.assertEqual(len(numbers), 999)
        self.assertTrue(all(0 <= n <= 1 for n in numbers))

    def test_random_uniform(self):
        rng = RandomNumberGenerator(predefined_nums=[0.5])
        result = rng.random_uniform(0, 10)
        self.assertEqual(result, 5)

    def test_linear_congruential_method(self):
        nums = [0] * 5
        linear_congruential_method(1664525, 2**32, 1013904223, 12345, nums, 5)
        self.assertEqual(len(nums), 5)
        self.assertNotEqual(nums[0], nums[1])  # Ensure numbers are changing

    def test_out_of_numbers(self):
        rng = RandomNumberGenerator(predefined_nums=[0.5])
        rng.random_uniform(0, 1)
        with self.assertRaises(Exception):  # Should raise an OutOfRandomNumbersError
            rng.random_uniform(0, 1)


if __name__ == "__main__":
    unittest.main()
