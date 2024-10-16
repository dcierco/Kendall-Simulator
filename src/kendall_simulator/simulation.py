# kendall-simulator/src/simulation.py
"""
Simulation module for the Kendall Queue Network Simulator.

This module contains the core classes and logic for simulating a network of queues.
It defines the Event, Queue, and Simulation classes, which together form the backbone
of the queue network simulation system.

Key components:
    - Event: Represents different types of events in the simulation.
    - Queue: Models individual queues with their properties and behaviors.
    - Simulation: Orchestrates the overall simulation process.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Union
import heapq
import logging
from kendall_simulator.random_generator import RandomNumberGenerator
from kendall_simulator.exceptions import (
    InvalidQueueConfigurationError,
    InvalidEventError,
    OutOfRandomNumbersError,
)

logger = logging.getLogger(__name__)


@dataclass(order=True)
class Event:
    """
    Represents an event in the simulation.

    Attributes:
        time: The time at which the event occurs.
        event_type: The type of event ('arrival', 'departure', or 'passage').
        origin_queue: The queue where the event originates.
        destination_queue: The destination queue for passage events.
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
        name: The name of the queue.
        servers: The number of servers in the queue.
        arrival_time: The min and max arrival times.
        service_time: The min and max service times.
        capacity: The maximum number of clients the queue can hold. If None, capacity is infinite.
        network: The network of connected queues and their probabilities.
        arrival_start_time: Time when the simulator will start generating arrivals, if None, it will not start.
        clients: The current number of clients in the queue.
        time_at_service: Time spent at each possible state (number of clients).
        losses: The number of clients lost due to queue being at capacity.
        kendall_notation: The Kendall notation for the queue.
    """

    name: str
    servers: int
    service_time: Tuple[float, float]
    arrival_time: Optional[Tuple[float, float]] = None
    capacity: Optional[Union[int, float]] = None
    network: Optional[List[Tuple[Optional["Queue"], float]]] = None
    arrival_start_time: Optional[float] = None
    clients: int = 0
    time_at_service: List[float] = field(init=False)
    losses: int = 0
    kendall_notation: str = field(init=False)

    def __post_init__(self):
        """Initialize the Queue object and perform validation checks."""
        logger.info(f"Initializing Queue {self.name}")
        self._validate_configuration()
        self._initialize_attributes()

    def _validate_configuration(self):
        """Validate the queue configuration."""
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

    def _initialize_attributes(self):
        """Initialize additional attributes of the queue."""
        self.capacity = float("inf") if self.capacity is None else self.capacity
        self.time_at_service = [0] * (
            int(self.capacity) + 1 if isinstance(self.capacity, int) else 1
        )
        self.kendall_notation = self._generate_kendall_notation()
        logger.debug(
            f"Queue {self.name} initialized with Kendall notation: {self.kendall_notation}"
        )

    def _generate_kendall_notation(self) -> str:
        """
        Generate the Kendall notation for the queue.

        Returns:
            The Kendall notation string (A/B/C/K/N/D format).
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
        time: The current simulation time.
        queues_list: The list of queues in the simulation.
        rng: The random number generator.
        events: The list of scheduled events.
    """

    def __init__(self, rng: RandomNumberGenerator, queues_list: List[Queue]):
        """
        Initialize the Simulation.

        Args:
            rng: The random number generator to use.
            queues_list: The list of queues in the simulation.
        """
        logger.info("Initializing Simulation")
        self.time: float = 0
        self.queues_list: List[Queue] = queues_list
        self.rng: RandomNumberGenerator = rng
        self.events: List[Event] = []
        self._initialize_events()

    def _initialize_events(self):
        """Initialize events for queues with external arrivals."""
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
        event_index = 0

        try:
            while self.events:
                event = heapq.heappop(self.events)
                self._process_event(event, event_index)
                event_index += 1

                if not self.rng.hasNext():
                    logger.warning("Ran out of random numbers. Stopping simulation.")
                    break

        except InvalidEventError as e:
            logger.error(f"Simulation error: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")

        self._log_simulation_summary()

    def _process_event(self, event: Event, event_index: int):
        """
        Process a single event in the simulation.

        Args:
            event: The event to process.
            event_index: The index of the current event.
        """
        logger.debug(
            f"Processing event: ({event_index}) {event.event_type}, {self.time:.4f}, -"
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
                raise InvalidEventError(f"Unknown event type: {event.event_type}")
        except OutOfRandomNumbersError:
            logger.warning("Ran out of random numbers during event processing.")
            raise

        self._log_event_details(event_index)

    def _log_event_details(self, event_index: int):
        """
        Log details about the current state of the simulation.

        Args:
            event_index: The index of the current event.
        """
        logger.debug(f"\nEnd of the iteration {event_index}.")
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

    def _log_simulation_summary(self):
        """Log a summary of the simulation results."""
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
            event: The arrival event to process.
        """
        self.accumulate_time(event)
        queue = event.origin_queue

        if self._can_accept_client(queue):
            queue.clients += 1
            self._handle_client_acceptance(queue)
        else:
            logger.debug(f"Client arrived at full queue {queue.name}")
            queue.losses += 1

        self.schedule_event("arrival", queue)

    def _can_accept_client(self, queue: Queue) -> bool:
        """
        Check if the queue can accept a new client.

        Args:
            queue: The queue to check.

        Returns:
            True if the queue can accept a new client, False otherwise.
        """
        return queue.capacity is None or queue.clients < queue.capacity

    def _handle_client_acceptance(self, queue: Queue):
        """
        Handle the acceptance of a new client in the queue.

        Args:
            queue: The queue that accepted the client.
        """
        if queue.clients <= queue.servers:
            next_queue = self.select_next_queue(queue)
            if next_queue is not None:
                self.schedule_event(
                    "passage", queue=queue, destination_queue=next_queue
                )
            else:
                self.schedule_event("departure", queue)
        else:
            logger.debug("Not scheduled a passage/departure since the server is busy")

    def process_departure(self, event: Event):
        """
        Process a departure event.

        Args:
            event: The departure event to process.
        """
        self.accumulate_time(event)
        queue = event.origin_queue

        queue.clients -= 1
        if queue.clients >= queue.servers:
            self.schedule_event("departure", queue)

    def process_passage(self, event: Event):
        """
        Process a passage event (client moving from one queue to another).

        Args:
            event: The passage event to process.
        """
        self.accumulate_time(event)
        origin_queue = event.origin_queue
        dest_queue = event.destination_queue

        if dest_queue is not None:
            self._handle_passage(origin_queue, dest_queue)
        else:
            raise InvalidEventError("Destination queue is None")

    def _handle_passage(self, origin_queue: Queue, dest_queue: Queue):
        """
        Handle the passage of a client from one queue to another.

        Args:
            origin_queue: The queue the client is leaving.
            dest_queue: The queue the client is entering.
        """
        logging.debug(f"Passage from {origin_queue.name} to {dest_queue.name}")
        origin_queue.clients -= 1
        if origin_queue.clients >= origin_queue.servers:
            self.schedule_event(
                "passage", queue=origin_queue, destination_queue=dest_queue
            )

        if self._can_accept_client(dest_queue):
            dest_queue.clients += 1
            if dest_queue.clients <= dest_queue.servers:
                self._handle_client_acceptance(dest_queue)
        else:
            dest_queue.losses += 1

    def schedule_event(
        self, event_type: str, queue: Queue, destination_queue: Optional[Queue] = None
    ):
        """
        Schedule a new event.

        Args:
            event_type: The type of event to schedule.
            queue: The queue associated with the event.
            destination_queue: The destination queue for passage events.

        Raises:
            OutOfRandomNumbersError: If there are no more random numbers available.
            ValueError: If an invalid event type is provided.
        """
        try:
            time = self._calculate_event_time(event_type, queue)
            event = Event(time, event_type, queue, destination_queue)
            heapq.heappush(self.events, event)
            logger.debug(
                f"Scheduled {event_type} event for {queue.name} at time {time:.4f}"
                + (f" to {destination_queue.name}" if destination_queue else "")
            )
        except OutOfRandomNumbersError:
            logger.warning(
                f"Could not schedule {event_type} event for {queue.name} due to lack of random numbers"
            )
            raise

    def _calculate_event_time(self, event_type: str, queue: Queue) -> float:
        """
        Calculate the time for a new event.

        Args:
            event_type: The type of event.
            queue: The queue associated with the event.

        Returns:
            The calculated time for the event.

        Raises:
            ValueError: If an invalid event type is provided.
        """
        r = self.rng.random_uniform(0, 1)
        if event_type == "arrival" and queue.arrival_time is not None:
            return (
                self.time
                + queue.arrival_time[0]
                + (queue.arrival_time[1] - queue.arrival_time[0]) * r
            )
        elif event_type in ["departure", "passage"]:
            return (
                self.time
                + queue.service_time[0]
                + (queue.service_time[1] - queue.service_time[0]) * r
            )
        else:
            raise ValueError(f"Invalid event type: {event_type}")

    def select_next_queue(self, queue: Queue) -> Optional[Queue]:
        """
        Select the next queue for a client based on the network probabilities.

        Args:
            queue: The current queue.

        Returns:
            The selected next queue, or None if the client departs the system.
        """
        if queue.network is not None and len(queue.network) > 0:
            logger.debug(f"Selecting next queue from {queue.name}")

            if len(queue.network) == 1 and queue.network[0][1] == 1.0:
                # If there's only one next queue with 100% probability, return it directly
                return queue.network[0][0]

            try:
                r = self.rng.random_uniform(0, 1)
            except OutOfRandomNumbersError:
                logger.warning(
                    "Could not select next queue due to lack of random numbers"
                )
                raise

            return self._select_queue_based_on_probability(queue.network, r)
        else:
            logger.debug("No queue selected, this should be a departure event")
            return None

    def _select_queue_based_on_probability(
        self, network: List[Tuple[Optional[Queue], float]], r: float
    ) -> Optional[Queue]:
        """
        Select a queue based on the given probability.

        Args:
            network: List of tuples containing queues and their probabilities.
            r: Random number for probability comparison.

        Returns:
            The selected queue, or None if no queue is selected.
        """
        cumulative_prob: float = 0.0
        for next_queue, prob in network:
            cumulative_prob += prob
            if r < cumulative_prob:
                return next_queue
        return None

    def accumulate_time(self, event: Event):
        """
        Accumulate time for all queues based on the current event.

        Args:
            event: The current event being processed.
        """
        new_time = event.time
        delta = new_time - self.time

        for queue in self.queues_list:
            current_state = queue.clients
            queue.time_at_service[current_state] += delta

        self.time = new_time
