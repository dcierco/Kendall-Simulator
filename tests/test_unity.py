import unittest
from simulation import Queue, Event
from random_generator import RandomNumberGenerator

class TestQueue(unittest.TestCase):
    def test_queue_initialization(self):
        queue = Queue("Test Queue", 2, (1, 3), (5, 6), capacity=4)
        self.assertEqual(queue.name, "Test Queue")
        self.assertEqual(queue.servers, 2)
        self.assertEqual(queue.capacity, 4)
        self.assertEqual(queue.arrival_time, (1, 3))
        self.assertEqual(queue.service_time, (5, 6))
        self.assertEqual(len(queue.time_at_service), 5)  # capacity + 1

    def test_kendall_notation(self):
        queue1 = Queue("Q1", 2, (1, 3), (5, 6), capacity=4)
        self.assertEqual(queue1.kendall_notation, "G/G/2/4/∞/FCFS")

        queue2 = Queue("Q2", 1, (2, 2), (4, 4), capacity=3)
        self.assertEqual(queue2.kendall_notation, "D/D/1/3/∞/FCFS")

        queue3 = Queue("Q3", 3, (0, 0), (2, 4), capacity=5, has_external_arrivals=False)
        self.assertEqual(queue3.kendall_notation, "G/G/3/5/∞/FCFS")

class TestEvent(unittest.TestCase):
    def test_event_ordering(self):
        queue = Queue("Test Queue", 2, (1, 3), (5, 6), capacity=4)
        event1 = Event(10, "arrival", queue)
        event2 = Event(20, "departure", queue)
        event3 = Event(10, "passage", queue, queue)

        self.assertLess(event1, event2)
        self.assertEqual(event1, event3)  # Same time, different type should be equal
        self.assertLess(event1, Event(11, "arrival", queue))

class TestRandomNumberGenerator(unittest.TestCase):
    def test_random_uniform(self):
        rng = RandomNumberGenerator(quantity=100, seed=42)
        for _ in range(100):
            r = rng.random_uniform(0, 1)
            self.assertIsNotNone(r)
            if r is not None:
                self.assertGreaterEqual(r, 0.0)
                self.assertLessEqual(r, 1.0)

        # Test if None is returned when out of numbers
        self.assertIsNone(rng.random_uniform(0, 1))

    def test_random_uniform_range(self):
        rng = RandomNumberGenerator(quantity=100, seed=42)
        a, b = 10, 20
        for _ in range(100):
            r = rng.random_uniform(a, b)
            self.assertIsNotNone(r)
            if r is not None:
                self.assertGreaterEqual(r, a)
                self.assertLessEqual(r, b)

if __name__ == '__main__':
    unittest.main()
