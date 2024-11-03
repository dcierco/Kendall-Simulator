# kendall-simulator/tests/test_simulator.py
import unittest
import os
import tempfile
import yaml
import logging
from src.kendall_simulator.simulator import (
    load_config,
    _create_single_queue,
    _setup_network_connections,
    _initialize_random_number_generator,
    main,
)


class TestSimulator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

    def test_load_config(self):
        """Test configuration loading from YAML file."""
        # Create test config file
        config = {
            "seed": 42,
            "quantityNums": 100,
            "queuesList": [
                {
                    "name": "Q1",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                }
            ],
        }
        config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Test loading
        loaded_config = load_config(config_path)
        self.assertEqual(loaded_config["seed"], 42)
        self.assertEqual(loaded_config["quantityNums"], 100)

    def test_load_config_file_not_found(self):
        """Test error handling for missing config file."""
        with self.assertRaises(SystemExit):
            load_config("nonexistent.yaml")

    def test_create_single_queue(self):
        """Test creation of a single queue from config."""
        queue_config = {
            "name": "Q1",
            "servers": 2,
            "serviceTimeMin": 1.0,
            "serviceTimeMax": 2.0,
            "arrivalTimeMin": 0.5,
            "arrivalTimeMax": 1.5,
            "capacity": 5,
            "arrivalStartTime": 0.0,
        }
        queue = _create_single_queue(queue_config)

        self.assertEqual(queue.name, "Q1")
        self.assertEqual(queue.servers, 2)
        self.assertEqual(queue.service_time, (1.0, 2.0))
        self.assertEqual(queue.arrival_time, (0.5, 1.5))
        self.assertEqual(queue.capacity, 5)

    def test_setup_network_connections(self):
        """Test setting up network connections between queues."""
        config = {
            "queuesList": [
                {
                    "name": "Q1",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                    "network": [["Q2", 0.7], ["Q3", 0.3]],
                },
                {
                    "name": "Q2",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                },
                {
                    "name": "Q3",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                },
            ]
        }

        queues_dict = {}
        for q_config in config["queuesList"]:
            queues_dict[q_config["name"]] = _create_single_queue(q_config)

        _setup_network_connections(config, queues_dict)

        # Verify network connections
        self.assertIsNotNone(queues_dict["Q1"].network)
        self.assertEqual(len(queues_dict["Q1"].network), 2)
        self.assertEqual(queues_dict["Q1"].network[0][1], 0.7)  # probability check

    def test_initialize_random_generator_predefined(self):
        """Test random generator initialization with predefined numbers."""
        config = {"numbers": [0.1, 0.2, 0.3], "seed": 42}
        rng = _initialize_random_number_generator(config)
        self.assertTrue(rng.use_predefined)
        self.assertEqual(rng.quantity, 3)

    def test_initialize_random_generator_quantity(self):
        """Test random generator initialization with quantity."""
        config = {"quantityNums": 100, "seed": 42}
        rng = _initialize_random_number_generator(config)
        self.assertFalse(rng.use_predefined)
        self.assertEqual(rng.quantity, 100)

    def test_initialize_random_generator_error(self):
        """Test error handling for invalid random generator configuration."""
        config = {"seed": 42}  # Missing both numbers and quantityNums
        with self.assertRaises(ValueError):
            _initialize_random_number_generator(config)

    def test_main_execution(self):
        """Test main function execution with a simple configuration."""
        # Create test config
        config = {
            "seed": 42,
            "quantityNums": 10,
            "queuesList": [
                {
                    "name": "Q1",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                    "arrivalTimeMin": 0.5,
                    "arrivalTimeMax": 1.5,
                    "arrivalStartTime": 0.0,
                }
            ],
        }
        config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        # Create output directory
        output_dir = os.path.join(self.test_dir.name, "output")

        # Run main function
        main(config_path, output_dir, logging.ERROR)

        # Verify output files were created
        self.assertTrue(
            os.path.exists(os.path.join(output_dir, "simulation_results.txt"))
        )
        self.assertTrue(os.path.exists(os.path.join(output_dir, "sequence_plot.png")))
        self.assertTrue(
            os.path.exists(os.path.join(output_dir, "distribution_plot.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(output_dir, "generated_numbers.txt"))
        )


if __name__ == "__main__":
    unittest.main()
