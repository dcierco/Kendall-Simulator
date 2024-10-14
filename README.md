# 🚦 Kendall Queue Network Simulator

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output](#output)
- [Dispersion Graph](#dispersion-graph)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

The Kendall Queue Network Simulator is a powerful tool designed to model and analyze complex queueing systems. It allows users to simulate networks of queues with various configurations, providing insights into system behavior, bottlenecks, and performance metrics.

This simulator is particularly useful for:
- 🏭 Manufacturing process optimization
- 🏥 Healthcare facility capacity planning
- 🖥️ Computer network performance analysis
- 🛒 Retail checkout system design

## ✨ Features

- 🔗 Support for interconnected queue networks
- 📊 Customizable queue parameters (servers, capacity, arrival/service times)
- 🔢 Deterministic mode for reproducible simulations
- 📈 Detailed state probability calculations
- 📉 Loss rate analysis
- 🧮 Kendall notation inference
- 📊 Dispersion graph generation for random numbers
- 🔄 Flexible random number generation and usage

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kendall-queue-simulator.git
   cd kendall-queue-simulator
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Create a configuration file (e.g., `my_config.yaml`) based on the example in `examples/example_config.yaml`.

2. Run the simulation:

```
python src/simulator.py my_config.yaml
```

3. View the results in the console output.

## ⚙️ Configuration

The configuration file (YAML format) is used to define your queue network. Here's an example:

```yaml
quantityNums: 10000
seed: 42
numbers: [0.1, 0.2, 0.3, 0.4, 0.5]  # Optional: for deterministic mode
queuesList:
  - name: Queue1
    servers: 2
    capacity: 4
    arrivalTimeMin: 1
    arrivalTimeMax: 3
    serviceTimeMin: 5
    serviceTimeMax: 6
    arrivalStartTime: 0
    network:
      - [Queue2, 0.7]
      - [Queue1, 0.2]
  # Add more queues as needed
```

- `quantityNums`: Number of random numbers to generate (if not using predefined numbers)
- `seed`: Random seed for reproducibility (optional, default is 69)
- `numbers`: (Optional) List of predefined random numbers for deterministic simulations
- `queuesList`: List of queues in the network, each with its own parameters

Queue parameters:
- `name`: Unique name for the queue
- `servers`: Number of servers in the queue
- `capacity`: Maximum number of clients (optional, infinite if not specified)
- `arrivalTimeMin` and `arrivalTimeMax`: Range for arrival times
- `serviceTimeMin` and `serviceTimeMax`: Range for service times
- `arrivalStartTime`: Time when external arrivals start (optional)
- `network`: List of next queues and their probabilities (optional)

## 📊 Output

The simulator provides detailed output for each queue, including:
- Kendall notation
- Time spent in each state
- Probability of each state
- Number of losses (rejected clients)

It also shows the total simulation time, overall losses, and a summary of unprocessed events.

## 📊 Dispersion Graph

To generate a dispersion graph of the random numbers:

1. In `random_generator.py`, uncomment these lines at the bottom:
   ```python
   # x = list(range(len(numbers)))
   # generate_graph(x, numbers)
   ```

2. Run the simulation. The graph will be displayed after completion.

This graph helps visualize the distribution and quality of the generated random numbers.

## 🧪 Testing

To run the tests:

```
python -m unittest discover tests
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
