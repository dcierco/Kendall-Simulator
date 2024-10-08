import yaml
from typing import Dict, Any, List, Optional
from simulation import Simulation, Queue

def load_config(file_path: str) -> Dict[str, Any]:
    """
    Loads the configuration from a YAML file.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration.
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """
    The main function that runs the simulation.
    It loads the configuration, sets up the queues, runs the simulation,
    and prints the results.
    """
    # Load configuration
    config = load_config("config.yaml")

    # Extract simulation parameters
    initial_time = config['initialTime']
    quantity_nums = config['quantityNums']
    seed = config['seed']
    predefined_nums: Optional[List[float]] = config.get('numbers')

    # Create queues
    queues_dict: Dict[str, Queue] = {}
    for q_config in config['queuesList']:
        queue = Queue(
            q_config['name'],
            q_config['servers'],
            q_config['capacity'],
            (q_config['arrivalTimeMin'], q_config['arrivalTimeMax']),
            (q_config['serviceTimeMin'], q_config['serviceTimeMax']),
            has_external_arrivals=q_config.get('hasExternalArrivals', True)
        )
        queues_dict[queue.name] = queue

    # Set up network connections
    for q_config in config['queuesList']:
        queue = queues_dict[q_config['name']]
        queue.network = [(queues_dict[next_q], prob) for next_q, prob in q_config['network']]

    queues_list = list(queues_dict.values())

    # Initialize and run simulation
    sim = Simulation(initial_time, quantity_nums, seed, queues_list, predefined_nums)
    sim.execute()

    # Print results
    for queue in sim.queues_list:
        print(f'Queue: {queue.name} ({queue.kendall_notation}):')
        total_time = sum(queue.time_at_service)
        for index, time in enumerate(queue.time_at_service):
            if time > 0:
                probability = round((time / total_time) * 100, 4)
                print(f'State: {index}, Time: {time}, Probability: {probability}%')
        print(f'Losses: {queue.losses}')
        print()

    print(f'Simulation time: {sim.time} seconds')
    print(f'Total losses: {sim.losses}')

if __name__ == "__main__":
    main()
