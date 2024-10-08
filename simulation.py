from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import heapq
from randomGen import GeneratedNums

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
        capacity (int): The maximum number of clients the queue can hold.
        arrival_time (Tuple[float, float]): The min and max arrival times.
        service_time (Tuple[float, float]): The min and max service times.
        network (List[Tuple[Queue, float]]): The network of connected queues and their probabilities.
        has_external_arrivals (bool): Whether the queue has external arrivals.
        clients (int): The current number of clients in the queue.
        time_at_service (List[float]): Time spent at each possible state (number of clients).
        losses (int): The number of clients lost due to queue being at capacity.
        kendall_notation (str): The Kendall notation for the queue.
    """
    name: str
    servers: int
    capacity: int
    arrival_time: Tuple[float, float]
    service_time: Tuple[float, float]
    network: List[Tuple['Queue', float]] = field(default_factory=list)
    has_external_arrivals: bool = True
    clients: int = 0
    time_at_service: List[float] = field(init=False)
    losses: int = 0
    kendall_notation: str = field(init=False)

    def __post_init__(self):
        self.time_at_service = [0] * (self.capacity + 1)
        self.kendall_notation = self.generate_kendall_notation()

    def generate_kendall_notation(self) -> str:
        """
        Generates the Kendall notation for the queue.

        Returns:
            str: The Kendall notation string.
        """
        # Infer arrival distribution (A)
        if not self.has_external_arrivals:
            A = "G"  # General distribution for internal arrivals
        elif self.arrival_time[0] == self.arrival_time[1]:
            A = "D"  # Deterministic if min == max
        else:
            A = "G"  # General distribution otherwise

        # Infer service distribution (B)
        if self.service_time[0] == self.service_time[1]:
            B = "D"  # Deterministic if min == max
        else:
            B = "G"  # General distribution otherwise

        C = str(self.servers)
        K = str(self.capacity)
        N = "∞"  # Assuming infinite population
        D = "FCFS"  # Assuming First-Come-First-Served policy

        return f"{A}/{B}/{C}/{K}/{N}/{D}"

class Simulation:
    """
    Represents the main simulation engine.

    Attributes:
        time (float): The current simulation time.
        quantity_nums (int): The number of random numbers to generate/use.
        seed (int): The seed for random number generation.
        queues_list (List[Queue]): The list of queues in the simulation.
        losses (int): The total number of losses across all queues.
        random_nums (List[float]): The list of random numbers to use.
        random_index (int): The current index in the random number list.
        events (List[Event]): The list of scheduled events.
        previous_time (float): The time of the previous event.
    """

    def __init__(self, initial_time: float, quantity_nums: int, seed: int, queues_list: List[Queue], predefined_nums: Optional[List[float]] = None):
        self.time = initial_time
        self.queues_list = queues_list
        self.losses = 0

        # Use predefined numbers if provided, otherwise generate random numbers
        if predefined_nums is not None:
            self.random_nums = predefined_nums
            self.quantity_nums = len(predefined_nums)
        else:
            self.quantity_nums = quantity_nums
            self.random_nums = GeneratedNums(quantity_nums, seed).getNums()

        self.random_index = 0
        self.events: List[Event] = []
        self.previous_time = initial_time

        # Schedule initial arrivals for queues with external arrivals
        for queue in self.queues_list:
            if queue.has_external_arrivals:
                self.schedule_arrival(queue)

    def execute(self):
        """
        Executes the simulation until the stop condition is met.
        """
        while self.random_index < self.quantity_nums and self.events:
            event = heapq.heappop(self.events)
            self.time = event.time

            if event.event_type == 'arrival':
                self.process_arrival(event)
            elif event.event_type == 'departure':
                self.process_departure(event)
            elif event.event_type == 'passage':
                self.process_passage(event)

    def process_arrival(self, event: Event):
        """
        Processes an arrival event.

        Args:
            event (Event): The arrival event to process.
        """
        queue = event.origin_queue
        self.accumulate_time()

        if queue.clients < queue.capacity:
            queue.clients += 1
            if queue.clients <= queue.servers:
                self.schedule_service_completion(queue)
        else:
            queue.losses += 1
            self.losses += 1

        if queue.has_external_arrivals:
            self.schedule_arrival(queue)

    def process_departure(self, event: Event):
        """
        Processes a departure event.

        Args:
            event (Event): The departure event to process.
        """
        queue = event.origin_queue
        self.accumulate_time()

        queue.clients -= 1
        if queue.clients >= queue.servers:
            self.schedule_service_completion(queue)

    def process_passage(self, event: Event):
        """
        Processes a passage event (client moving from one queue to another).

        Args:
            event (Event): The passage event to process.
        """
        origin_queue = event.origin_queue
        dest_queue = event.destination_queue
        self.accumulate_time()

        origin_queue.clients -= 1
        if origin_queue.clients >= origin_queue.servers:
            self.schedule_service_completion(origin_queue)

        if dest_queue is not None:
            if dest_queue.clients < dest_queue.capacity:
                dest_queue.clients += 1
                if dest_queue.clients <= dest_queue.servers:
                    self.schedule_service_completion(dest_queue)
            else:
                dest_queue.losses += 1
                self.losses += 1
        else:
            self.losses += 1

    def schedule_arrival(self, queue: Queue):
        """
        Schedules an arrival event for the given queue.

        Args:
            queue (Queue): The queue for which to schedule an arrival.
        """
        arrival_time = self.time + self.random_uniform(queue.arrival_time[0], queue.arrival_time[1])
        heapq.heappush(self.events, Event(arrival_time, 'arrival', queue))

    def schedule_service_completion(self, queue: Queue):
        """
        Schedules a service completion event for the given queue.

        Args:
            queue (Queue): The queue for which to schedule a service completion.
        """
        service_time = self.random_uniform(queue.service_time[0], queue.service_time[1])
        completion_time = self.time + service_time

        next_queue = self.select_next_queue(queue)

        if next_queue is None:
            heapq.heappush(self.events, Event(completion_time, 'departure', queue))
        else:
            heapq.heappush(self.events, Event(completion_time, 'passage', queue, next_queue))

    def select_next_queue(self, queue: Queue) -> Optional[Queue]:
        """
        Selects the next queue for a client based on the network probabilities.

        Args:
            queue (Queue): The current queue.

        Returns:
            Optional[Queue]: The selected next queue, or None if the client departs the system.
        """
        if not queue.network:
            return None

        r = self.random_uniform(0, 1)
        cumulative_prob = 0
        for next_queue, prob in queue.network:
            cumulative_prob += prob
            if r < cumulative_prob:
                return next_queue

        # If we reach here, it means the probabilities didn't sum to 1
        # We'll default to the last queue in the network
        return queue.network[-1][0]

    def accumulate_time(self):
        """
        Accumulates time spent in the current state for all queues.
        """
        delta = self.time - self.previous_time
        for queue in self.queues_list:
            queue.time_at_service[queue.clients] += delta
        self.previous_time = self.time

    def random_uniform(self, a: float, b: float) -> float:
        """
        Generates a random number uniformly distributed between a and b.

        Args:
            a (float): The lower bound of the range.
            b (float): The upper bound of the range.

        Returns:
            float: A random number between a and b.

        Raises:
            Exception: If we run out of random numbers.
        """
        if self.random_index >= len(self.random_nums):
            raise Exception("Ran out of random numbers")
        r = self.random_nums[self.random_index]
        self.random_index += 1
        return a + (b - a) * r
