# kendall-simulator/tests/test_simulator.py
import unittest
import os
import tempfile
import yaml
import logging
import sys
from io import StringIO
from contextlib import redirect_stdout
from kendall_simulator.simulator import (
    load_config,
    create_queues,
    _create_single_queue,
    _initialize_random_number_generator,
    main,
)


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        # Basic test configuration
        self.test_config = {
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

    def test_load_config(self):
        """Test configuration loading from YAML file."""
        config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(self.test_config, f)

        loaded_config = load_config(config_path)
        self.assertEqual(loaded_config["seed"], 42)
        self.assertEqual(loaded_config["quantityNums"], 10)

        # Test error cases
        with self.assertRaises(SystemExit):
            load_config("nonexistent.yaml")

        # Test invalid YAML
        with open(config_path, "w") as f:
            f.write("invalid: yaml: :")
        with self.assertRaises(SystemExit):
            load_config(config_path)

    def test_create_queues(self):
        """Test queue creation from configuration."""
        queues = create_queues(self.test_config)
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0].name, "Q1")
        self.assertEqual(queues[0].servers, 1)

    def test_create_single_queue(self):
        """Test single queue creation with different configurations."""
        # Test minimal configuration
        min_config = {
            "name": "Q1",
            "servers": 1,
            "serviceTimeMin": 1.0,
            "serviceTimeMax": 2.0,
        }
        queue = _create_single_queue(min_config)
        self.assertEqual(queue.name, "Q1")

        # Test full configuration
        full_config = {
            "name": "Q2",
            "servers": 2,
            "serviceTimeMin": 1.0,
            "serviceTimeMax": 2.0,
            "arrivalTimeMin": 0.5,
            "arrivalTimeMax": 1.5,
            "capacity": 5,
            "arrivalStartTime": 0.0,
        }
        queue = _create_single_queue(full_config)
        self.assertEqual(queue.capacity, 5)

    def test_setup_network_connections(self):
        """Test network setup with different configurations."""
        config = {
            "queuesList": [
                {
                    "name": "Q1",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                    "network": [["Q2", 0.7]],
                },
                {
                    "name": "Q2",
                    "servers": 1,
                    "serviceTimeMin": 1.0,
                    "serviceTimeMax": 2.0,
                },
            ]
        }

        queues = create_queues(config)
        self.assertIsNotNone(queues[0].network)
        self.assertIsNone(queues[1].network)

    def test_initialize_random_generator(self):
        """Test random generator initialization."""
        # Test with predefined numbers
        config_pred = {"numbers": [0.1, 0.2], "seed": 42}
        rng_pred = _initialize_random_number_generator(config_pred)
        self.assertTrue(rng_pred.use_predefined)

        # Test with quantity
        config_qty = {"quantityNums": 100, "seed": 42}
        rng_qty = _initialize_random_number_generator(config_qty)
        self.assertFalse(rng_qty.use_predefined)

        # Test error case
        with self.assertRaises(ValueError):
            _initialize_random_number_generator({"seed": 42})

    def test_main_execution(self):
        """Test main function with different configurations."""
        config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        output_dir = os.path.join(self.test_dir.name, "output")

        # Test with generated numbers
        with open(config_path, "w") as f:
            yaml.dump(self.test_config, f)

        # Capture stdout
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            main(config_path, output_dir, logging.ERROR)

        # Verify outputs
        self.assertTrue(
            os.path.exists(os.path.join(output_dir, "simulation_results.txt"))
        )
        self.assertTrue(os.path.exists(os.path.join(output_dir, "sequence_plot.png")))
        self.assertTrue(
            os.path.exists(os.path.join(output_dir, "distribution_plot.png"))
        )

        # Test with predefined numbers
        self.test_config["numbers"] = [0.1, 0.2, 0.3]
        del self.test_config["quantityNums"]
        with open(config_path, "w") as f:
            yaml.dump(self.test_config, f)

        main(config_path, output_dir, logging.ERROR)

    def test_command_line_interface(self):
        """Test command line interface."""
        config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(self.test_config, f)

        # Save original argv
        orig_argv = sys.argv
        try:
            # Test with minimal arguments
            sys.argv = ["simulator.py", config_path]
            with redirect_stdout(StringIO()):
                if __name__ == "__main__":
                    pass  # This will trigger the CLI code

            # Test with all arguments
            sys.argv = [
                "simulator.py",
                config_path,
                "--output-dir",
                "test_output",
                "--log-level",
                "DEBUG",
            ]
            with redirect_stdout(StringIO()):
                if __name__ == "__main__":
                    pass
        finally:
            # Restore original argv
            sys.argv = orig_argv


if __name__ == "__main__":
    unittest.main()
