# kendall-simulator/tests/test_random_generator.py
import unittest
import os
import time
import tempfile
from kendall_simulator.random_generator import RandomNumberGenerator


class TestRandomNumberGenerator(unittest.TestCase):
    def test_predefined_numbers(self):
        """Test that predefined numbers are returned in order."""
        numbers = [0.1, 0.2, 0.3, 0.4, 0.5]
        rng = RandomNumberGenerator(predefined_nums=numbers)

        generated = []
        for _ in range(len(numbers)):
            generated.append(rng.get_next_random())

        self.assertEqual(generated, numbers)
        self.assertEqual(rng.generated_nums, numbers)

    def test_parallel_lcm_generation(self):
        """Test that parallel LCM generates correct numbers."""
        quantity = 100
        buffer_size = 10
        rng = RandomNumberGenerator(seed=42, quantity=quantity, buffer_size=buffer_size)

        # Generate all numbers
        numbers = []
        while rng.hasNext():
            numbers.append(rng.get_next_random())

        # Verify results
        self.assertEqual(len(numbers), quantity)
        self.assertTrue(all(0 <= n <= 1 for n in numbers))
        self.assertTrue(len(set(numbers)) > 1)
        self.assertEqual(rng.generated_nums, numbers)

    def test_buffer_size_handling(self):
        """Test that buffer size limits are respected."""
        buffer_size = 5
        rng = RandomNumberGenerator(seed=42, quantity=20, buffer_size=buffer_size)

        # Check that we can get numbers even with small buffer
        numbers = []
        while rng.hasNext():
            numbers.append(rng.get_next_random())
            # Verify queue never exceeds buffer size
            self.assertLessEqual(rng.number_queue.qsize(), buffer_size)

        self.assertEqual(len(numbers), 20)

    def test_seed_reproducibility(self):
        """Test that same seed produces same sequence in parallel generation."""
        seed = 42
        quantity = 50

        rng1 = RandomNumberGenerator(seed=seed, quantity=quantity)
        rng2 = RandomNumberGenerator(seed=seed, quantity=quantity)

        nums1 = []
        nums2 = []

        while rng1.hasNext() and rng2.hasNext():
            nums1.append(rng1.get_next_random())
            nums2.append(rng2.get_next_random())

        self.assertEqual(nums1, nums2)

    def test_parallel_generation_speed(self):
        """Test that parallel generation doesn't block main thread significantly."""
        quantity = 1000
        rng = RandomNumberGenerator(seed=42, quantity=quantity)

        start_time = time.time()
        first_number = rng.get_next_random()
        time_to_first = time.time() - start_time

        # First number should be available almost immediately
        self.assertLess(time_to_first, 0.1)
        self.assertTrue(0 <= first_number <= 1)

    def test_quantity_limit_generation(self):
        """Test that generator produces exactly the requested quantity of numbers."""
        quantity = 10
        rng = RandomNumberGenerator(seed=42, quantity=quantity)

        numbers = []
        for _ in range(quantity):
            self.assertTrue(rng.hasNext())
            number = rng.get_next_random()
            self.assertTrue(0 <= number <= 1)
            numbers.append(number)

        self.assertEqual(len(numbers), quantity)
        self.assertFalse(rng.hasNext())

    def test_thread_safety(self):
        """Test thread-safe access to generated numbers list."""
        quantity = 100
        rng = RandomNumberGenerator(seed=42, quantity=quantity)

        # Generate numbers rapidly to try to expose race conditions
        numbers = []
        while rng.hasNext():
            numbers.append(rng.get_next_random())

        # Verify no duplicates in generated_nums (which would indicate race condition)
        self.assertEqual(len(rng.generated_nums), len(set(rng.generated_nums)))
        self.assertEqual(len(rng.generated_nums), quantity)

    def test_output_files(self):
        """Test file output functionality with parallel generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            quantity = 50
            rng = RandomNumberGenerator(seed=42, quantity=quantity)

            # Generate all numbers
            numbers = []
            while rng.hasNext():
                numbers.append(rng.get_next_random())

            # Test writing numbers to file
            rng.write_numbers_to_file(tmpdir)
            with open(os.path.join(tmpdir, "generated_numbers.txt")) as f:
                written_numbers = [float(line.strip()) for line in f]
            self.assertEqual(written_numbers, numbers)

            # Test generating graphs
            rng.generate_dispersion_graph(tmpdir)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "sequence_plot.png")))
            self.assertTrue(
                os.path.exists(os.path.join(tmpdir, "distribution_plot.png"))
            )

    def test_invalid_initialization(self):
        """Test that initialization fails without required parameters."""
        with self.assertRaises(ValueError):
            RandomNumberGenerator()  # No quantity or predefined_nums

        # These should work
        RandomNumberGenerator(quantity=10)
        RandomNumberGenerator(predefined_nums=[0.1, 0.2])


if __name__ == "__main__":
    unittest.main()
