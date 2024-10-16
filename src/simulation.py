"""
Simulation module for the Kendall Queue Network Simulator.

This module contains the core classes and logic for simulating a network of queues.
It defines the Event, Queue, and Simulation classes, which together form the backbone
of the queue network simulation system.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union
import heapq
import logging
from random_generator import RandomNumberGenerator
from exceptions import (
    InvalidQueueConfigurationError,
    InvalidEventError,
    OutOfRandomNumbersError,
)

# Setting up logger
logger = logging.getLogger(__name__)


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
    origin_queue: "Queue" = field(compare=False)
    destination_queue: Optional["Queue"] = field(default=None, compare=False)

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
        network (List[Tuple[Optional[Queue], float]]): The network of connected queues and their probabilities.
        arrival_start_time (Optional[float]): Time when the simulator will start generating arrivals, if None, it will not start.
        clients (int): The current number of clients in the queue.
        time_at_service (List[float]): Time spent at each possible state (number of clients).
        losses (int): The number of clients lost due to queue being at capacity.
        kendall_notation (str): The Kendall notation for the queue.
    """

    name: str
    servers: int
    service_time: Tuple[float, float]
    arrival_time: Optional[Tuple[float, float]] = None
    capacity: Optional[Union[int, float]] = None
    network: List[Tuple[Optional["Queue"], float]] = field(default_factory=list)
    arrival_start_time: Optional[float] = None
    clients: int = 0
    time_at_service: List[float] = field(init=False)
    losses: int = 0
    kendall_notation: str = field(init=False)

    def __post_init__(self):
        logger.info(f"Initializing Queue {self.name}")
        if self.servers <= 0:
            logger.error(
                f"Invalid number of servers for Queue {self.name}: {self.servers}"
            )
            raise InvalidQueueConfigurationError(
                f"Queue {self.name} must have at least one server"
            )
        if self.arrival_time and self.arrival_time[0] > self.arrival_time[1]:
            logger.error(
                f"Invalid arrival time range for Queue {self.name}: {self.arrival_time}"
            )
            raise InvalidQueueConfigurationError(
                f"Queue {self.name} has invalid arrival time range"
            )
        if self.service_time[0] > self.service_time[1]:
            logger.error(
                f"Invalid service time range for Queue {self.name}: {self.service_time}"
            )
            raise InvalidQueueConfigurationError(
                f"Queue {self.name} has invalid service time range"
            )

        self.capacity = float("inf") if self.capacity is None else self.capacity
        self.time_at_service = [0] * (
            int(self.capacity) + 1 if isinstance(self.capacity, int) else 1
        )
        self.kendall_notation = self.generate_kendall_notation()
        logger.debug(
            f"Queue {self.name} initialized with Kendall notation: {self.kendall_notation}"
        )

    def generate_kendall_notation(self) -> str:
        """
        Generate the Kendall notation for the queue.

        Returns:
            str: The Kendall notation string (A/B/C/K/N/D format).
        """
        A = (
            "D"
            if self.arrival_time and self.arrival_time[0] == self.arrival_time[1]
            else "G"
        )
        B = "D" if self.service_time[0] == self.service_time[1] else "G"
        C = str(self.servers)
        K = str(int(self.capacity)) if isinstance(self.capacity, int) else "∞"
        N = "∞"
        D = "FCFS"
        return f"{A}/{B}/{C}/{K}/{N}/{D}"


class Simulation:
    """
    Represents the main simulation engine.

    This class orchestrates the simulation of the queue network, managing events,
    time progression, and statistics collection.

    Attributes:
        time (float): The current simulation time.
        queues_list (List[Queue]): The list of queues in the simulation.
        losses (int): The total number of losses across all queues.
        rng (RandomNumberGenerator): The random number generator.
        events (List[Event]): The list of scheduled events.
        previous_time (float): The time of the previous event.
    """

    def __init__(self, rng: RandomNumberGenerator, queues_list: List[Queue]):
        """
        Initialize the Simulation.

        Args:
            rng: The random number generator to use.
            queues_list: The list of queues in the simulation.
        """
        logger.info("Initializing Simulation")
        self.time = 0
        self.queues_list = queues_list
        self.losses = 0
        self.rng = rng
        self.events: List[Event] = []
        self.previous_time = 0

        # Initialize events for queues with external arrivals
        for queue in self.queues_list:
            if queue.arrival_start_time is not None and queue.arrival_time is not None:
                initial_arrival_time = queue.arrival_start_time
                initial_event = Event(initial_arrival_time, "arrival", queue)
                heapq.heappush(self.events, initial_event)
                logger.debug(
                    f"Initialized arrival event for {queue.name} at time {initial_arrival_time:.4f}"
                )

    def execute(self):
        """
        Execute the simulation until running out of random numbers.

        This method processes events in chronological order, updating the state
        of the queues and collecting statistics until no more random numbers are available.
        """
        logger.debug("Starting simulation execution")
        eventIndex = 0

        try:
            while self.events:
                event = heapq.heappop(self.events)

                # Update the simulation time to the event time
                self.accumulate_time(event)

                logger.debug(
                    f"Processing event: ({eventIndex}) {event.event_type}, {self.time:.4f}, -"
                )

                try:
                    if event.event_type == "arrival":
                        self.process_arrival(event)
                    elif event.event_type == "departure":
                        self.process_departure(event)
                    elif event.event_type == "passage":
                        self.process_passage(event)
                    else:
                        logger.error(f"Invalid event type: {event.event_type}")
                        raise InvalidEventError(
                            f"Unknown event type: {event.event_type}"
                        )
                except OutOfRandomNumbersError:
                    logger.warning("Ran out of random numbers. Stopping simulation.")
                    break
                finally:
                    eventIndex += 1
                    logger.debug(f"\nEnd of the iteration {eventIndex}.")
                    logger.debug(f"Simulation global time: {self.time:.4f}")
                    logger.debug("Events on the scheduler: ")
                    for event in self.events:
                        logger.debug(f"Event {event.event_type} at time {event.time}")

                    for queue in self.queues_list:
                        logger.debug(f"Queue: {queue.name} ({queue.kendall_notation}):")
                        for index, time in enumerate(queue.time_at_service):
                            if time > 0:
                                logger.debug(f"State: {index}, Time: {time:.4f}")
                        logger.debug(f"Clients: {queue.clients}")
                        logger.debug(f"Losses: {queue.losses}\n")

        except InvalidEventError as e:
            logger.error(f"Simulation error: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")

        logger.info("Simulation execution completed")
        logger.debug(f"Random numbers used: {self.rng.index}")
        logger.debug(f"Remaining events: {len(self.events)}")
        logger.debug(f"Last processed event time: {self.time:.4f}")

        for event in self.events:
            logger.debug(
                f"  Unprocessed event: type={event.event_type}, time={event.time:.4f}, queue={event.origin_queue.name}"
            )

    def process_arrival(self, event: Event):
        """
        Process an arrival event.

        Args:
            event (Event): The arrival event to process.
        """
        queue = event.origin_queue

        if queue.capacity is None or queue.clients < queue.capacity:
            queue.clients += 1
            if queue.clients <= queue.servers:
                self.schedule_event("departure", queue)
        else:
            queue.losses += 1
            self.losses += 1

        if queue.arrival_time is not None:
            self.schedule_event("arrival", queue)

    def process_departure(self, event: Event):
        """
        Process a departure event.

        Args:
            event (Event): The departure event to process.
        """
        queue = event.origin_queue

        queue.clients -= 1
        if queue.clients >= queue.servers:
            self.schedule_event("departure", queue)

        next_queue = self.select_next_queue(queue)
        if next_queue:
            self.schedule_event("passage", queue, destination_queue=next_queue)

    def process_passage(self, event: Event):
        """
        Process a passage event (client moving from one queue to another).

        Args:
            event (Event): The passage event to process.
        """
        origin_queue = event.origin_queue
        dest_queue = event.destination_queue

        origin_queue.clients -= 1
        if origin_queue.clients >= origin_queue.servers:
            self.schedule_event("departure", origin_queue)

        if dest_queue is not None:
            if dest_queue.capacity is None or dest_queue.clients < dest_queue.capacity:
                dest_queue.clients += 1
                if dest_queue.clients <= dest_queue.servers:
                    self.schedule_event("departure", dest_queue)
            else:
                dest_queue.losses += 1
                self.losses += 1
        else:
            self.losses += 1

    def schedule_event(
        self, event_type: str, queue: Queue, destination_queue: Optional[Queue] = None
    ):
        try:
            if event_type == "arrival" and queue.arrival_time is not None:
                r = self.rng.random_uniform(0, 1)
                time = (
                    self.time
                    + queue.arrival_time[0]
                    + (queue.arrival_time[1] - queue.arrival_time[0]) * r
                )
            elif event_type in ["departure", "passage"]:
                r = self.rng.random_uniform(0, 1)
                time = (
                    self.time
                    + queue.service_time[0]
                    + (queue.service_time[1] - queue.service_time[0]) * r
                )
            else:
                raise ValueError(f"Invalid event type: {event_type}")

            event = Event(time, event_type, queue, destination_queue)
            heapq.heappush(self.events, event)
            logger.debug(
                f"Scheduled {event_type} event for {queue.name} at time {time:.4f}"
            )
        except OutOfRandomNumbersError:
            logger.warning(
                f"Could not schedule {event_type} event for {queue.name} due to lack of random numbers"
            )
            raise

    def select_next_queue(self, queue: Queue) -> Optional[Queue]:
        """
        Select the next queue for a client based on the network probabilities.

        Args:
            queue (Queue): The current queue.

        Returns:
            Optional[Queue]: The selected next queue, or None if the client departs the system.
        """
        logger.debug(f"Selecting next queue from {queue.name}")
        if not queue.network:
            return None

        r = self.rng.random_uniform(0, 1)
        if r is None:
            logger.warning("Could not select next queue due to lack of random numbers")
            return None

        cumulative_prob: float = 0.0
        for next_queue, prob in queue.network:
            cumulative_prob += prob
            if r < cumulative_prob:
                return next_queue

        return None  # Client leaves the system if no queue is selected

    def accumulate_time(self, event: Event):
        """
        Accumulate time spent in the current state for all queues.

        Args:
            event (Event): The current event being processed.
        """
        delta = event.time - self.time
        for queue in self.queues_list:
            queue.time_at_service[queue.clients] += delta
        self.time = event.time
