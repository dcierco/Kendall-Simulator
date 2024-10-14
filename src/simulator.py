"""
Kendall Queue Network Simulator

This script runs a simulation of a network of queues based on a configuration file.
It supports both predefined random numbers and generated random numbers for the simulation.

Usage:
    python simulator.py <config_file>

Example:
    python simulator.py config.yaml
"""

import logging
import sys
import yaml
from typing import Dict, Any, List, Optional, Tuple, cast
from simulation import Simulation, Queue
from random_generator import RandomNumberGenerator


def setup_logging(log_level):
    """
    Set the logger for the app

    Args:

    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging set up with level: {log_level}")


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load the configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the specified file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Loading configuration from {file_path}")
    try:
        with open(file_path, "r") as f:
            return cast(Dict[str, Any], yaml.safe_load(f))
    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing the configuration file: {e}")
        sys.exit(1)


def create_queues(config: Dict[str, Any]) -> List[Queue]:
    """
    Create Queue objects based on the configuration.

    Args:
        config (Dict[str, Any]): The configuration dictionary.

    Returns:
        List[Queue]: A list of Queue objects.
    """
    logger = logging.getLogger(__name__)
    logger.info("Creating queues from configuration")
    queues_dict: Dict[str, Queue] = {}
    for q_config in config["queuesList"]:
        queue = Queue(
            q_config["name"],
            q_config["servers"],
            (q_config["arrivalTimeMin"], q_config["arrivalTimeMax"]),
            (q_config["serviceTimeMin"], q_config["serviceTimeMax"]),
            capacity=q_config.get("capacity"),
            arrival_start_time=q_config.get("arrivalStartTime"),
        )
        queues_dict[queue.name] = queue

    # Set up network connections
    for q_config in config["queuesList"]:
        queue = queues_dict[q_config["name"]]
        if "network" in q_config:
            network: List[Tuple[Optional[Queue], float]] = [
                (queues_dict[next_q], prob) for next_q, prob in q_config["network"]
            ]
            total_prob = sum(prob for _, prob in network)
            if total_prob < 1:
                network.append(
                    (None, 1 - total_prob)
                )  # Probability of leaving the system
            queue.network = network
        else:
            queue.network = [(None, 1.0)]  # Clients leave after service

    return list(queues_dict.values())


def main(input_file: str):
    """
    Run the queue network simulation based on the provided input file with the configuration of the queues.

    Args:
        input_file (str): Path to the simulator configuration file.
    """
    setup_logging(logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting simulation with input file: {input_file}")

    config = load_config(input_file)

    # Extract simulation parameters
    predefined_nums: Optional[List[float]] = config.get("numbers")
    quantity_nums: Optional[int] = config.get("quantityNums")
    seed: int = config.get("seed", 69)

    logger.info(
        f"Simulation parameters: predefined_nums={predefined_nums is not None}, quantity_nums={quantity_nums}, seed={seed}"
    )

    # Initialize random number generator
    if predefined_nums is not None:
        logger.info("Using predefined random numbers")
        rng = RandomNumberGenerator(predefined_nums=predefined_nums)
    elif quantity_nums is not None:
        logger.info(f"Generating {quantity_nums} random numbers with seed {seed}")
        rng = RandomNumberGenerator(quantity=quantity_nums, seed=seed)
    else:
        logger.error(
            "Neither 'numbers' nor 'quantityNums' defined in the configuration"
        )
        raise ValueError(
            "Either 'numbers' or 'quantityNums' must be defined in the configuration."
        )

    # Create queues
    queues_list = create_queues(config)

    # Initialize and run simulation
    logger.info("Initializing and running simulation")
    sim = Simulation(rng, queues_list)
    sim.execute()

    # Print results
    logger.info("Printing simulation results")
    for queue in sim.queues_list:
        print(f"Queue: {queue.name} ({queue.kendall_notation}):")
        total_time = sum(queue.time_at_service)
        for index, time in enumerate(queue.time_at_service):
            if time > 0:
                probability = round((time / total_time) * 100, 4)
                print(f"State: {index}, Time: {time}, Probability: {probability}%")
        print(f"Losses: {queue.losses}")
        print()

    print(f"Simulation time: {sim.time} seconds")
    print(f"Total losses: {sim.losses}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simulator.py <config_file>")
        sys.exit(1)
    main(sys.argv[1])
