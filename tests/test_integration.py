import unittest
import yaml
from simulation import Simulation, Queue
from random_generator import RandomNumberGenerator

class TestSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('tests/test_config.yaml', 'r') as f:
            cls.config = yaml.safe_load(f)

    def setUp(self):
        self.queues = {}
        for q_config in self.config['queuesList']:
            queue = Queue(
                q_config['name'],
                q_config['servers'],
                (q_config['arrivalTimeMin'], q_config['arrivalTimeMax']),
                (q_config['serviceTimeMin'], q_config['serviceTimeMax']),
                capacity=q_config['capacity'],
                has_external_arrivals=q_config.get('hasExternalArrivals', True)
            )
            self.queues[q_config['name']] = queue

        for q_config in self.config['queuesList']:
            queue = self.queues[q_config['name']]
            queue.network = [(self.queues[next_q], prob) for next_q, prob in q_config['network']]

    def run_simulation(self):
        sim = Simulation(
            self.config['initialTime'],
            self.config.get('quantityNums', 0),  # This will be ignored if predefined_nums is provided
            self.config.get('seed', 0),  # This will be ignored if predefined_nums is provided
            list(self.queues.values()),
            self.config['numbers']
        )
        sim.execute()
        return sim

    def test_simulation_execution(self):
        sim = self.run_simulation()
        self.assertGreater(sim.time, 0)
        self.assertGreaterEqual(sim.losses, 0)

        for queue in sim.queues_list:
            self.assertGreaterEqual(queue.clients, 0)
            if queue.capacity is not None:
                self.assertLessEqual(queue.clients, queue.capacity)
            self.assertGreaterEqual(queue.losses, 0)
            self.assertGreater(sum(queue.time_at_service), 0)

    def test_network_flow(self):
        sim = self.run_simulation()
        self.assertGreater(self.queues['Queue2'].clients, 0)
        self.assertGreater(self.queues['Queue3'].clients, 0)

if __name__ == '__main__':
    unittest.main()
