from typing import List
import matplotlib.pyplot as plt

def linear_congruential_method(a: int, m: int, c: int, x0: int, random_nums: List[int], num_of_random_nums: int) -> None:
    """
    Generate random numbers using the linear congruential method.

    Args:
        a (int): Multiplier
        m (int): Modulus
        c (int): Increment
        x0 (int): Seed
        random_nums (List[int]): List to store generated numbers
        num_of_random_nums (int): Number of random numbers to generate
    """
    random_nums[0] = x0

    for i in range(1, num_of_random_nums):
        random_nums[i] = ((random_nums[i-1] * a) + c) % m

def print_nums(random_nums: List[float]) -> None:
    """
    Print the generated random numbers.

    Args:
        random_nums (List[float]): List of random numbers
    """
    for num in random_nums:
        print(num, end=' ')

def normalize_nums(max_num: int, random_nums: List[int]) -> List[float]:
    """
    Normalize the generated random numbers.

    Args:
        max_num (int): Maximum value in the random_nums list
        random_nums (List[int]): List of random numbers

    Returns:
        List[float]: Normalized list of random numbers
    """
    return [round(num / max_num, 4) for num in random_nums]

def generate_graph(x: List[int], y: List[float]) -> None:
    """
    Generate a graph of the random numbers.

    Args:
        x (List[int]): List of indices
        y (List[float]): List of random numbers
    """
    plt.scatter(x, y)
    plt.title('Pseudo-random generated numbers')
    plt.xlabel('Generated number index')
    plt.ylabel('Generated number')
    plt.show()

def write_nums_to_file(file_name: str, content: List[float]) -> None:
    """
    Write the random numbers to a file.

    Args:
        file_name (str): Name of the file to write to
        content (List[float]): List of random numbers to write
    """
    with open(file_name, 'w') as f:
        for num in content:
            f.write(f"{num}\n")

class RandomNumberGenerator:
    """
    A class to generate and manage random numbers.
    """

    def __init__(self, quantity: int, seed: int):
        """
        Initialize the RandomNumberGenerator.

        Args:
            quantity (int): Number of random numbers to generate
            seed (int): Seed for the random number generation
        """
        self.quantity = quantity + 1
        self.seed = seed
        self.a = 214013
        self.m = 4294967296
        self.c = 2531011
        self.nums = self._generate_numbers()

    def _generate_numbers(self) -> List[float]:
        """
        Generate the random numbers.

        Returns:
            List[float]: List of generated random numbers
        """
        random_nums = [0] * self.quantity
        linear_congruential_method(self.a, self.m, self.c, self.seed, random_nums, self.quantity)
        max_num = max(random_nums[1:])
        return normalize_nums(max_num, random_nums[1:])

    def get_nums(self) -> List[float]:
        """
        Get the generated random numbers.

        Returns:
            List[float]: List of generated random numbers
        """
        return self.nums

    def write_to_file(self, file_name: str = "generated_numbers.txt") -> None:
        """
        Write the generated numbers to a file.

        Args:
            file_name (str, optional): Name of the file to write to. Defaults to "generated_numbers.txt".
        """
        write_nums_to_file(file_name, self.nums)

if __name__ == '__main__':
    # Example usage
    generator = RandomNumberGenerator(quantity=1000, seed=346)
    numbers = generator.get_nums()
    print_nums(numbers[:10])  # Print first 10 numbers
    generator.write_to_file()

    # Uncomment to generate graph
    # x = list(range(len(numbers)))
    # generate_graph(x, numbers)
