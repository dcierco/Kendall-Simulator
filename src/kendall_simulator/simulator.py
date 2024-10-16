# kendall-simulator/src/simulator.py
"""
Kendall Queue Network Simulator

This script runs a simulation of a network of queues based on a configuration file.
It supports both predefined random numbers and generated random numbers for the simulation.

Usage:
    python simulator.py <config_file>

Example:
    python simulator.py config.yaml

This module serves as the main entry point for running simulations. It handles
configuration loading, queue creation, and simulation execution.
"""

import argparse
import logging
import sys
import yaml
from typing import Dict, Any, List, Optional, Tuple, cast
from kendall_simulator.simulation import Simulation, Queue
from kendall_simulator.random_generator import RandomNumberGenerator


def setup_logging(log_level: int) -> None:
    """
    Set up the logger for the application.

    Args:
        log_level: The logging level to use.
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging set up with level: {logging.getLevelName(log_level)}")


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load the configuration from a YAML file.

    Args:
        file_path: Path to the YAML configuration file.

    Returns:
        A dictionary containing the configuration.

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
        logger.error(f"Configuration file '{file_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing the configuration file: {e}")
        sys.exit(1)


def create_queues(config: Dict[str, Any]) -> List[Queue]:
    """
    Create Queue objects based on the configuration.

    Args:
        config: The configuration dictionary.

    Returns:
        A list of Queue objects.
    """
    logger = logging.getLogger(__name__)
    logger.info("Creating queues from configuration")
    queues_dict: Dict[str, Queue] = {}

    for q_config in config["queuesList"]:
        queue = _create_single_queue(q_config)
        queues_dict[queue.name] = queue

    _setup_network_connections(config, queues_dict)

    return list(queues_dict.values())


def _create_single_queue(q_config: Dict[str, Any]) -> Queue:
    """
    Create a single Queue object from its configuration.

    Args:
        q_config: Configuration for a single queue.

    Returns:
        A Queue object.
    """
    queue_args = {
        "name": q_config["name"],
        "servers": q_config["servers"],
        "service_time": (q_config["serviceTimeMin"], q_config["serviceTimeMax"]),
        "capacity": q_config.get("capacity"),
    }
    if "arrivalTimeMin" in q_config and "arrivalTimeMax" in q_config:
        queue_args["arrival_time"] = (
            q_config["arrivalTimeMin"],
            q_config["arrivalTimeMax"],
        )
    if "arrivalStartTime" in q_config:
        queue_args["arrival_start_time"] = q_config["arrivalStartTime"]

    return Queue(**queue_args)


def _setup_network_connections(
    config: Dict[str, Any], queues_dict: Dict[str, Queue]
) -> None:
    """
    Set up network connections between queues.

    Args:
        config: The full configuration dictionary.
        queues_dict: Dictionary of created Queue objects.
    """
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
            queue.network = (
                None  # Clients always leave after service if no network is defined
            )


def main(input_file: str, log_level: int = logging.INFO) -> None:
    """
    Run the queue network simulation based on the provided input file.

    Args:
        input_file: Path to the simulator configuration file.
        log_level: Logging level to use. Defaults to logging.INFO.
    """
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Starting simulation with input file: {input_file}")

    config = load_config(input_file)
    rng = _initialize_random_number_generator(config)
    queues_list = create_queues(config)

    logger.info("Initializing and running simulation")
    sim = Simulation(rng, queues_list)
    sim.execute()

    _print_simulation_results(sim)


def _initialize_random_number_generator(
    config: Dict[str, Any]
) -> RandomNumberGenerator:
    """
    Initialize the random number generator based on configuration.

    Args:
        config: The configuration dictionary.

    Returns:
        An initialized RandomNumberGenerator object.

    Raises:
        ValueError: If neither 'numbers' nor 'quantityNums' is defined in the configuration.
    """
    logger = logging.getLogger(__name__)
    predefined_nums: Optional[List[float]] = config.get("numbers")
    quantity_nums: Optional[int] = config.get("quantityNums")
    seed: int = config.get("seed", 69)

    logger.info(
        f"Simulation parameters: predefined_nums={predefined_nums is not None}, quantity_nums={quantity_nums}, seed={seed}"
    )

    if predefined_nums is not None:
        logger.info("Using predefined random numbers")
        return RandomNumberGenerator(predefined_nums=predefined_nums)
    elif quantity_nums is not None:
        logger.info(f"Generating {quantity_nums} random numbers with seed {seed}")
        return RandomNumberGenerator(quantity=quantity_nums, seed=seed)
    else:
        logger.error(
            "Neither 'numbers' nor 'quantityNums' defined in the configuration"
        )
        raise ValueError(
            "Either 'numbers' or 'quantityNums' must be defined in the configuration."
        )


def _print_simulation_results(sim: Simulation) -> None:
    """
    Print the results of the simulation.

    Args:
        sim: The completed Simulation object.
    """
    logger = logging.getLogger(__name__)
    total_losses = 0
    logger.info("Printing simulation results")

    for queue in sim.queues_list:
        print(f"Queue: {queue.name} ({queue.kendall_notation}):")
        total_time = sum(queue.time_at_service)
        for index, time in enumerate(queue.time_at_service):
            if time > 0:
                probability = round((time / total_time) * 100, 4)
                print(f"State: {index}, Time: {time}, Probability: {probability}%")
        if logger.level == 0:
            print(f"Number of remaining clients: {queue.clients}")
        print(f"Losses: {queue.losses}")
        total_losses += queue.losses

    print(f"Simulation time: {sim.time} seconds")
    print(f"Total losses: {total_losses}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Kendall Queue Network Simulator."
    )
    parser.add_argument("config_file", help="Path to the configuration file")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    log_level = getattr(logging, args.log_level.upper())
    main(args.config_file, log_level=log_level)
