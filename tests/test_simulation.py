# kendall-simulator/tests/test_simulation.py
import unittest
from kendall_simulator.simulation import Simulation, Queue, Event
from kendall_simulator.random_generator import RandomNumberGenerator


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.rng = RandomNumberGenerator(
            predefined_nums=[0.5, 0.3, 0.7, 0.1, 0.9, 0.4, 0.6, 0.2, 0.8]
        )
        self.queue1 = Queue(
            "Q1", 1, (1.0, 2.0), (2.0, 4.0), capacity=3, arrival_start_time=0.0
        )
        self.queue2 = Queue("Q2", 2, (3.0, 5.0), capacity=4)
        self.queue3 = Queue("Q3", 1, (1.0, 3.0), capacity=2)
        self.simulation = Simulation(self.rng, [self.queue1, self.queue2, self.queue3])

    def test_queue_initialization(self):
        self.assertEqual(self.queue1.name, "Q1")
        self.assertEqual(self.queue1.servers, 1)
        self.assertEqual(self.queue1.capacity, 3)
        self.assertEqual(self.queue1.kendall_notation, "G/G/1/3/∞/FCFS")

    def test_accumulate_time(self):
        event = Event(time=1.5, event_type="arrival", origin_queue=self.queue1)
        self.simulation.accumulate_time(event)

        self.assertEqual(self.simulation.time, 1.5)
        self.assertEqual(self.queue1.time_at_service[0], 1.5)
        self.assertEqual(self.queue2.time_at_service[0], 1.5)
        self.assertEqual(self.queue3.time_at_service[0], 1.5)

    def test_process_arrival(self):
        event = Event(time=1.0, event_type="arrival", origin_queue=self.queue1)
        self.simulation.process_arrival(event)

        self.assertEqual(self.queue1.clients, 1)
        self.assertGreater(len(self.simulation.events), 0)

    def test_process_departure(self):
        self.queue1.clients = 1
        event = Event(time=2.0, event_type="departure", origin_queue=self.queue1)
        self.simulation.process_departure(event)

        self.assertEqual(self.queue1.clients, 0)

    def test_process_passage(self):
        self.queue1.clients = 1
        self.queue1.network = [(self.queue2, 1.0)]
        event = Event(
            time=2.0,
            event_type="passage",
            origin_queue=self.queue1,
            destination_queue=self.queue2,
        )
        self.simulation.process_passage(event)

        self.assertEqual(self.queue1.clients, 0)
        self.assertEqual(self.queue2.clients, 1)

    def test_select_next_queue(self):
        self.queue1.network = [(self.queue2, 0.7), (self.queue3, 0.3)]
        next_queue = self.simulation.select_next_queue(self.queue1)
        self.assertIn(next_queue, [self.queue2, self.queue3])

    def test_schedule_event(self):
        initial_events_count = len(self.simulation.events)
        self.simulation.schedule_event("arrival", self.queue1)
        self.assertEqual(len(self.simulation.events), initial_events_count + 1)

    def test_invalid_event_type(self):
        with self.assertRaises(ValueError):
            self.simulation.schedule_event("invalid_type", self.queue1)

    def test_time_consistency(self):
        self.simulation.execute()

        for queue in self.simulation.queues_list:
            total_queue_time = sum(queue.time_at_service)
            self.assertAlmostEqual(total_queue_time, self.simulation.time, places=6)

    def test_queue_capacity(self):
        for _ in range(5):  # Attempt to add more clients than capacity
            self.simulation.process_arrival(
                Event(time=1.0, event_type="arrival", origin_queue=self.queue1)
            )

        self.assertEqual(self.queue1.clients, self.queue1.capacity)
        self.assertEqual(self.queue1.losses, 2)


if __name__ == "__main__":
    unittest.main()
