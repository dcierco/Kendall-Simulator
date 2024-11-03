# kendall-simulator/src/kendall_simulator/random_generator.py
"""
Random Number Generator module for the Kendall Queue Network Simulator.

This module provides functionality for generating random numbers using the Linear
Congruential Method (LCM) in a parallel manner. It supports both on-demand generation
and predefined number sequences for reproducible simulations.

Key components:
    - RandomNumberGenerator: Main class for generating random numbers using parallel processing.
    - Supporting functions for visualization and analysis of generated numbers.

The Linear Congruential Method uses the formula:
    X_{n+1} = (a * X_n + c) mod M

where:
    a: multiplier (default: 214013)
    c: increment (default: 2531011)
    M: modulus (default: 2^32)
    X_0: seed
"""

import os
import time
import threading
from queue import Queue as ThreadQueue
from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt
import logging
from kendall_simulator.exceptions import OutOfRandomNumbersError

logger = logging.getLogger(__name__)


def generate_graph(x: List[int], y: List[float], output_dir: str) -> None:
    """
    Generate and save distribution plots of random numbers.

    Args:
        x: List of indices.
        y: List of random numbers.
        output_dir: Path to output directory.
    """
    # Convert to numpy arrays for better performance
    y_array = np.array(y)
    x_array = np.array(x)

    # Generate sequence plot
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)
    ax.scatter(x_array, y_array, s=1, alpha=0.1, c="black")
    ax.set_title(f"Random Number Sequence (n={len(y):,} points)")
    ax.set_xlabel("Generation Sequence")
    ax.set_ylabel("Generated Value")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)  # Set y-axis limits
    ax.set_xlim(0, len(x_array))  # Set x-axis limits
    plt.tight_layout(pad=0.5)
    plt.savefig(
        os.path.join(output_dir, "sequence_plot.png"),
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.close()

    # Generate histogram
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)
    counts, bins = np.histogram(y_array, bins=100)
    ax.hist(bins[:-1], bins, weights=counts, alpha=0.7)
    ax.set_title("Random Number Distribution")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)  # Set x-axis limits for histogram
    plt.tight_layout(pad=0.5)
    plt.savefig(
        os.path.join(output_dir, "distribution_plot.png"),
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.close()


def write_nums_to_file(file_path: str, numbers: List[float]) -> None:
    """
    Write a list of numbers to a file.

    Args:
        file_path: Path of the file to write to.
        numbers: List of numbers to write.
    """
    with open(file_path, "w") as f:
        for num in numbers:
            f.write(f"{num}\n")


class RandomNumberGenerator:
    """
    A class to generate random numbers using the Linear Congruential Method in parallel.

    This class implements a producer-consumer pattern where random numbers are generated
    in a separate thread and stored in a thread-safe queue. This allows for efficient
    number generation without blocking the main simulation thread.

    Attributes:
        a (int): Multiplier for the LCM (default: 214013).
        c (int): Increment for the LCM (default: 2531011).
        M (int): Modulus for the LCM (default: 2^32).
        previous (int): Current/previous generated number in the sequence.
        generated_nums (List[float]): List of all generated numbers for analysis.
        use_predefined (bool): Whether to use predefined numbers.
        quantity (int): Total number of random numbers to generate/use.
        number_queue (ThreadQueue): Thread-safe queue for number generation.
        numbers_generated (int): Count of numbers generated/consumed so far.
        _lock (threading.Lock): Lock for thread-safe operations.
    """

    def __init__(
        self,
        seed: int = 69,
        predefined_nums: Optional[List[float]] = None,
        quantity: Optional[int] = None,
        buffer_size: int = 1000,
    ):
        """
        Initialize the RandomNumberGenerator with parallel generation capabilities.

        Args:
            seed: Starting value for the random sequence. Defaults to 69.
            predefined_nums: Optional list of predefined random numbers.
            quantity: Maximum number of random numbers to generate.
                     Required if predefined_nums is None.
            buffer_size: Size of the number generation buffer. Defaults to 1000.
                       Only used when generating numbers (not with predefined_nums).

        Raises:
            ValueError: If neither quantity nor predefined_nums is provided.
        """
        logger.info(f"Initializing RandomNumberGenerator with seed {seed}")

        # LCM parameters
        self.a: int = 214013
        self.c: int = 2531011
        self.M: int = 4294967296  # 2^32
        self.previous: int = seed

        # Store generated numbers for analysis
        self.generated_nums: List[float] = []
        self._lock = threading.Lock()

        if predefined_nums is not None:
            logger.debug("Using predefined random number sequence")
            self.use_predefined = True
            self.predefined_nums = predefined_nums
            self.quantity = len(predefined_nums)
            self.number_queue = ThreadQueue()
            for num in predefined_nums:
                self.number_queue.put(num)
        elif quantity is not None:
            logger.debug(f"Using parallel LCM for generating {quantity} random numbers")
            self.use_predefined = False
            self.quantity = quantity
            self.number_queue = ThreadQueue(maxsize=buffer_size)
            self.generator_thread = threading.Thread(
                target=self._generate_numbers_thread, daemon=True
            )
            self.generator_thread.start()
        else:
            raise ValueError("Either quantity or predefined_nums must be provided")

        self.numbers_generated = 0

    def _generate_numbers_thread(self) -> None:
        """
        Generate random numbers in a separate thread.

        This method implements the producer part of the producer-consumer pattern.
        It continuously generates random numbers using LCM and puts them in the
        thread-safe queue until reaching the specified quantity.
        """
        local_previous = self.previous
        generated_count = 0

        while generated_count < self.quantity:
            # Generate next number using LCM
            local_previous = ((self.a * local_previous) + self.c) % self.M
            number = local_previous / self.M

            try:
                self.number_queue.put(number, timeout=1)
                generated_count += 1
                logger.debug(f"Generated number {generated_count}/{self.quantity}")
            except ThreadQueue.full:
                logger.debug("Number queue full, waiting...")
                time.sleep(0.1)

    def get_next_random(self) -> float:
        """
        Get the next random number from the sequence.

        This method implements the consumer part of the producer-consumer pattern.
        It retrieves the next available number from the thread-safe queue and
        maintains the list of generated numbers for analysis.

        Returns:
            A random float between 0 and 1.

        Raises:
            OutOfRandomNumbersError: If maximum number of random numbers has been reached
                                   or if failed to get next number from queue.
        """
        if self.numbers_generated >= self.quantity:
            logger.error("Maximum number of random numbers reached")
            raise OutOfRandomNumbersError("Maximum number of random numbers reached")

        try:
            number = self.number_queue.get(timeout=1)
            with self._lock:
                self.generated_nums.append(number)
                self.numbers_generated += 1
            logger.debug(
                f"Retrieved random number {self.numbers_generated}/{self.quantity}: {number}"
            )
            return number
        except ThreadQueue.empty:
            logger.error("Failed to get next random number from queue")
            raise OutOfRandomNumbersError("Failed to generate next random number")

    def hasNext(self) -> bool:
        """
        Check if more random numbers are available.

        Returns:
            True if more numbers can be generated/retrieved, False otherwise.
        """
        return self.numbers_generated < self.quantity

    def generate_dispersion_graph(self, output_dir: str) -> None:
        """
        Generate and save dispersion graphs of the generated random numbers.

        Args:
            output_dir: Directory where to save the graphs.
        """
        logger.info("Generating dispersion graphs")
        os.makedirs(output_dir, exist_ok=True)

        generate_graph(
            list(range(len(self.generated_nums))), self.generated_nums, output_dir
        )
        logger.debug("Dispersion graphs saved")

    def write_numbers_to_file(self, output_dir: str) -> None:
        """
        Write all generated numbers to a file.

        Args:
            output_dir: Directory where to save the numbers.
        """
        logger.info("Writing generated numbers to file")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_numbers.txt")

        write_nums_to_file(output_path, self.generated_nums)
        logger.debug(f"Generated numbers saved to {output_path}")
