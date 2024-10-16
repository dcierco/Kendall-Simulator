# 🚦 Kendall Queue Network Simulator

[![codecov](https://codecov.io/gh/dcierco/Kendall-Simulator/branch/main/graph/badge.svg?token=XAHrjieYqX)](https://codecov.io/gh/dcierco/Kendall-Simulator)

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

2. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```

3. Install dependencies and create a virtual environment:
   ```
   poetry install
   ```

4. Activate the virtual environment:
   ```
   poetry shell
   ```

## 🚀 Usage

1. Create a configuration file (e.g., `my_config.yaml`) based on the example in `tests/yaml/routing_queue.yaml`.

2. Run the simulation:

```
poetry run python -m kendall_simulator.simulator my_config.yaml
```

3. View the results in the console output.

## ⚙️ Configuration

The configuration file (YAML format) is used to define your queue network. Here's an example:

```yaml
numbers:
  - 0.2176
  - 0.0103
  # ... more numbers ...

queuesList:
  - name: Q1
    servers: 1
    capacity: 5
    arrivalTimeMin: 20.0
    arrivalTimeMax: 40.0
    serviceTimeMin: 10.0
    serviceTimeMax: 12.0
    arrivalStartTime: 45.0
    network:
      - [Q2, 0.78]
      - [Q3, 0.12]
  # Add more queues as needed
```

For a full explanation of configuration options, see the comments in the example files.

## 📊 Output

The simulator provides detailed output for each queue, including:
- Kendall notation
- Time spent in each state
- Probability of each state
- Number of losses (rejected clients)

It also shows the total simulation time and overall losses.

## 📊 Dispersion Graph

To generate a dispersion graph of the random numbers, uncomment the relevant lines in `random_generator.py` as described in the file comments.

## 🧪 Testing

To run the tests with coverage:

```
poetry run pytest --cov=kendall_simulator
```

To generate an HTML coverage report:

```
poetry run pytest --cov=kendall_simulator --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
