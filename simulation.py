from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import heapq
from random_generator import RandomNumberGenerator

@dataclass(order=True)
class Event:
    """
    Represents an event in the simulation.

    Attributes:
        time (float): The time at which the event occurs.
        event_type (str): The type of event ('arrival', 'departure', or 'passage').
        origin_queue (Queue): The queue where the event originates.
        destination_queue (Optional[Queue]): The destination queue for passage events.
    """
    time: float
    event_type: str = field(compare=False)
    origin_queue: 'Queue' = field(compare=False)
    destination_queue: Optional['Queue'] = field(default=None, compare=False)

    def __post_init__(self):
        self.sort_index = self.time

@dataclass
class Queue:
    """
    Represents a queue in the simulation.

    Attributes:
        name (str): The name of the queue.
        servers (int): The number of servers in the queue.
        arrival_time (Tuple[float, float]): The min and max arrival times.
        service_time (Tuple[float, float]): The min and max service times.
        capacity (Optional[int]): The maximum number of clients the queue can hold. If None, capacity is infinite.
        network (List[Tuple[Queue, float]]): The network of connected queues and their probabilities.
        has_external_arrivals (bool): Whether the queue has external arrivals.
        clients (int): The current number of clients in the queue.
        time_at_service (List[float]): Time spent at each possible state (number of clients).
        losses (int): The number of clients lost due to queue being at capacity.
        kendall_notation (str): The Kendall notation for the queue.
    """
    name: str
    servers: int
    arrival_time: Tuple[float, float]
    service_time: Tuple[float, float]
    capacity: Optional[int] = None
    network: List[Tuple['Queue', float]] = field(default_factory=list)
    has_external_arrivals: bool = True
    clients: int = 0
    time_at_service: List[float] = field(init=False)
    losses: int = 0
    kendall_notation: str = field(init=False)

    def __post_init__(self):
        self.time_at_service = [0] * (self.capacity + 1 if self.capacity is not None else 1)
        self.kendall_notation = self.generate_kendall_notation()

    def generate_kendall_notation(self) -> str:
        """
        Generates the Kendall notation for the queue.

        Returns:
            str: The Kendall notation string.
        """
        A = "G" if not self.has_external_arrivals or self.arrival_time[0] != self.arrival_time[1] else "D"
        B = "D" if self.service_time[0] == self.service_time[1] else "G"
        C = str(self.servers)
        K = str(self.capacity) if self.capacity is not None else "∞"
        N = "∞"  # Assuming infinite population
        D = "FCFS"  # Assuming First-Come-First-Served policy
        return f"{A}/{B}/{C}/{K}/{N}/{D}"

class Simulation:
    """
    Represents the main simulation engine.

    Attributes:
        time (float): The current simulation time.
        queues_list (List[Queue]): The list of queues in the simulation.
        losses (int): The total number of losses across all queues.
        rng (RandomNumberGenerator): The random number generator.
        events (List[Event]): The list of scheduled events.
        previous_time (float): The time of the previous event.
    """

    def __init__(self, initial_time: float, quantity_nums: int, seed: int, queues_list: List[Queue], predefined_nums: Optional[List[float]] = None):
        self.time = initial_time
        self.queues_list = queues_list
        self.losses = 0
        self.rng = RandomNumberGenerator(quantity_nums, seed, predefined_nums)
        self.events: List[Event] = []
        self.previous_time = initial_time

        for queue in self.queues_list:
            if queue.has_external_arrivals:
                self.schedule_arrival(queue)

    def execute(self):
        """
        Executes the simulation until the stop condition is met.
        """
        while self.events:
            event = heapq.heappop(self.events)
            self.time = event.time

            if event.event_type == 'arrival':
                if not self.process_arrival(event):
                    break
            elif event.event_type == 'departure':
                if not self.process_departure(event):
                    break
            elif event.event_type == 'passage':
                if not self.process_passage(event):
                    break

        print(f"Simulation ended at time {self.time}")

    def process_arrival(self, event: Event) -> bool:
        """
        Processes an arrival event.

        Args:
            event (Event): The arrival event to process.

        Returns:
            bool: True if processing should continue, False if simulation should stop.
        """
        queue = event.origin_queue
        self.accumulate_time()

        if queue.capacity is None or queue.clients < queue.capacity:
            queue.clients += 1
            if queue.clients <= queue.servers:
                if not self.schedule_service_completion(queue):
                    return False
        else:
            queue.losses += 1
            self.losses += 1

        if queue.has_external_arrivals:
            if not self.schedule_arrival(queue):
                return False
        return True

    def process_departure(self, event: Event) -> bool:
        """
        Processes a departure event.

        Args:
            event (Event): The departure event to process.

        Returns:
            bool: True if processing should continue, False if simulation should stop.
        """
        queue = event.origin_queue
        self.accumulate_time()

        queue.clients -= 1
        if queue.clients >= queue.servers:
            if not self.schedule_service_completion(queue):
                return False
        return True

    def process_passage(self, event: Event) -> bool:
        """
        Processes a passage event (client moving from one queue to another).

        Args:
            event (Event): The passage event to process.

        Returns:
            bool: True if processing should continue, False if simulation should stop.
        """
        origin_queue = event.origin_queue
        dest_queue = event.destination_queue
        self.accumulate_time()

        origin_queue.clients -= 1
        if origin_queue.clients >= origin_queue.servers:
            if not self.schedule_service_completion(origin_queue):
                return False

        if dest_queue is not None:
            if dest_queue.capacity is None or dest_queue.clients < dest_queue.capacity:
                dest_queue.clients += 1
                if dest_queue.clients <= dest_queue.servers:
                    if not self.schedule_service_completion(dest_queue):
                        return False
            else:
                dest_queue.losses += 1
                self.losses += 1
        else:
            self.losses += 1

        return True

    def schedule_arrival(self, queue: Queue) -> bool:
        """
        Schedules an arrival event for the given queue.

        Args:
            queue (Queue): The queue for which to schedule an arrival.

        Returns:
            bool: True if scheduling was successful, False if out of random numbers.
        """
        r = self.rng.random_uniform(queue.arrival_time[0], queue.arrival_time[1])
        if r is None:
            return False
        arrival_time = self.time + r
        heapq.heappush(self.events, Event(arrival_time, 'arrival', queue))
        return True

    def schedule_service_completion(self, queue: Queue) -> bool:
        """
        Schedules a service completion event for the given queue.

        Args:
            queue (Queue): The queue for which to schedule a service completion.

        Returns:
            bool: True if scheduling was successful, False if out of random numbers.
        """
        r = self.rng.random_uniform(queue.service_time[0], queue.service_time[1])
        if r is None:
            return False
        completion_time = self.time + r

        next_queue = self.select_next_queue(queue)
        if next_queue is None:
            heapq.heappush(self.events, Event(completion_time, 'departure', queue))
        else:
            heapq.heappush(self.events, Event(completion_time, 'passage', queue, next_queue))
        return True

    def select_next_queue(self, queue: Queue) -> Optional[Queue]:
        """
        Selects the next queue for a client based on the network probabilities.

        Args:
            queue (Queue): The current queue.

        Returns:
            Optional[Queue]: The selected next queue, or None if the client departs the system or out of random numbers.
        """
        if not queue.network:
            return None

        r = self.rng.random_uniform(0, 1)
        if r is None:
            return None
        cumulative_prob = 0
        for next_queue, prob in queue.network:
            cumulative_prob += prob
            if r < cumulative_prob:
                return next_queue

        return queue.network[-1][0]

    def accumulate_time(self):
        """
        Accumulates time spent in the current state for all queues.
        """
        delta = self.time - self.previous_time
        for queue in self.queues_list:
            queue.time_at_service[queue.clients] += delta
        self.previous_time = self.time
