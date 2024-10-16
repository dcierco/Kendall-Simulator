# kendall-simulator/src/random_generator.py
"""
Random Number Generator module for the Kendall Queue Network Simulator.

This module provides functionality for generating and managing random numbers
used in the simulation. It supports both predefined lists of random numbers
and generation of random numbers using the linear congruential method.

Key components:
    - RandomNumberGenerator: Main class for generating and managing random numbers.
    - linear_congruential_method: Function to generate random numbers using LCM.
    - Utility functions for normalizing, printing, and writing random numbers.
"""

from typing import List, Optional
import matplotlib.pyplot as plt
import logging
from kendall_simulator.exceptions import OutOfRandomNumbersError

logger = logging.getLogger(__name__)


def linear_congruential_method(
    a: int, m: int, c: int, x0: int, random_nums: List[int], num_of_random_nums: int
) -> None:
    """
    Generate random numbers using the linear congruential method.

    Args:
        a: Multiplier.
        m: Modulus.
        c: Increment.
        x0: Seed.
        random_nums: List to store generated numbers.
        num_of_random_nums: Number of random numbers to generate.
    """
    random_nums[0] = x0

    for i in range(1, num_of_random_nums):
        random_nums[i] = ((random_nums[i - 1] * a) + c) % m


def print_nums(random_nums: List[float]) -> None:
    """
    Print the generated random numbers.

    Args:
        random_nums: List of random numbers.
    """
    for num in random_nums:
        print(num, end=" ")


def normalize_nums(max_num: int, random_nums: List[int]) -> List[float]:
    """
    Normalize the generated random numbers.

    Args:
        max_num: Maximum value in the random_nums list.
        random_nums: List of random numbers.

    Returns:
        Normalized list of random numbers.
    """
    return [round(num / max_num, 4) for num in random_nums]


def generate_graph(x: List[int], y: List[float]) -> None:
    """
    Generate a graph of the random numbers.

    Args:
        x: List of indices.
        y: List of random numbers.
    """
    plt.scatter(x, y)
    plt.title("Pseudo-random generated numbers")
    plt.xlabel("Generated number index")
    plt.ylabel("Generated number")
    plt.show()


def write_nums_to_file(file_name: str, content: List[float]) -> None:
    """
    Write the random numbers to a file.

    Args:
        file_name: Name of the file to write to.
        content: List of random numbers to write.
    """
    with open(file_name, "w") as f:
        for num in content:
            f.write(f"{num}\n")


class RandomNumberGenerator:
    """
    A class to generate and manage random numbers for the simulation.

    This class can work with either predefined lists of random numbers or
    generate new random numbers using the linear congruential method.

    Attributes:
        seed: Seed for the random number generation.
        a: Multiplier for the linear congruential method.
        m: Modulus for the linear congruential method.
        c: Increment for the linear congruential method.
        index: Current index in the list of random numbers.
        nums: List of random numbers.
        quantity: Total number of random numbers.
    """

    def __init__(
        self,
        quantity: Optional[int] = None,
        seed: int = 69,
        predefined_nums: Optional[List[float]] = None,
    ):
        """
        Initialize the RandomNumberGenerator.

        Args:
            quantity: Number of random numbers to generate. Required if predefined_nums is None.
            seed: Seed for the random number generation. Defaults to 69.
            predefined_nums: List of predefined random numbers.

        Raises:
            ValueError: If neither quantity nor predefined_nums is provided.
        """
        logger.info(f"Initializing RandomNumberGenerator with seed {seed}")

        self.seed: int = seed
        self.a: int = 214013
        self.m: int = 4294967296
        self.c: int = 2531011
        self.index: int = 0

        if predefined_nums is not None:
            self.nums: List[float] = predefined_nums
            self.quantity: int = len(predefined_nums)
        elif quantity is not None:
            self.quantity = quantity
            self.nums = self._generate_numbers()
        else:
            raise ValueError("Either quantity or predefined_nums must be provided.")

    def _generate_numbers(self) -> List[float]:
        """
        Generate the random numbers using the linear congruential method.

        Returns:
            List of generated random numbers.
        """
        logger.debug(f"Generating {self.quantity} random numbers")

        random_nums = [0] * self.quantity
        linear_congruential_method(
            self.a, self.m, self.c, self.seed, random_nums, self.quantity
        )
        max_num = max(random_nums[1:])
        return normalize_nums(max_num, random_nums[1:])

    def get_nums(self) -> List[float]:
        """
        Get the generated random numbers.

        Returns:
            List of generated random numbers.
        """
        return self.nums

    def write_to_file(self, file_name: str = "generated_numbers.txt") -> None:
        """
        Write the generated numbers to a file.

        Args:
            file_name: Name of the file to write to. Defaults to "generated_numbers.txt".
        """
        write_nums_to_file(file_name, self.nums)

    def random_uniform(self, a: float, b: float) -> float:
        """
        Generates a random number uniformly distributed between a and b.

        Args:
            a: The lower bound of the range.
            b: The upper bound of the range.

        Returns:
            A random number between a and b.

        Raises:
            OutOfRandomNumbersError: If the generator runs out of random numbers.
        """
        if not self.hasNext():
            logger.warning("Ran out of random numbers")
            raise OutOfRandomNumbersError("Ran out of random numbers")
        r = self.nums[self.index]
        self.index += 1
        return a + (b - a) * r

    def hasNext(self) -> bool:
        """
        Check if there are more random numbers available.

        Returns:
            True if there are more random numbers, False otherwise.
        """
        return self.index < len(self.nums)


if __name__ == "__main__":
    # Example usage
    generator = RandomNumberGenerator(quantity=1000, seed=346)
    numbers = generator.get_nums()
    print_nums(numbers[:10])  # Print first 10 numbers
    generator.write_to_file()

    # Uncomment to generate graph
    # x = list(range(len(numbers)))
    # generate_graph(x, numbers)
