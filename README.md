# 🚦 Kendall Queue Network Simulator

[![codecov](https://codecov.io/gh/dcierco/Kendall-Simulator/branch/main/graph/badge.svg?token=XAHrjieYqX)](https://codecov.io/gh/dcierco/Kendall-Simulator)

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output Files](#output-files)
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
- 🔢 Two modes of operation:
  - Predefined numbers for reproducible simulations
  - On-demand number generation using Linear Congruential Method (LCM)
- 📈 Detailed state probability calculations
- 📉 Loss rate analysis
- 🧮 Kendall notation inference
- 📊 Visual analysis through sequence and distribution plots
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

1. Create a configuration file (e.g., `config.yaml`) following the format in `tests/yaml/routing_queue.yaml`.

2. Run the simulation:
   ```
   poetry run python -m kendall_simulator.simulator config.yaml [--output-dir OUTPUT_DIR] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
   ```

   Arguments:
   - `config.yaml`: Path to your configuration file
   - `--output-dir`: Directory for output files (default: "output")
   - `--log-level`: Logging level (default: INFO)

## ⚙️ Configuration

The configuration file (YAML format) supports two modes of operation:

1. Using predefined numbers:
```yaml
numbers:
  - 0.2176
  - 0.0103
  # ... more numbers ...
```

2. Using generated numbers:
```yaml
quantityNums: 100000  # Number of random numbers to generate
seed: 42              # Seed for reproducibility
```

Queue configuration:
```yaml
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

## 📂 Output Files

The simulator generates several output files in the specified output directory:

1. `simulation_results.txt`: Detailed simulation results including:
   - Queue states and their probabilities
   - Time spent in each state
   - Loss statistics
   - Total simulation time

2. `sequence_plot.png`: Visual representation of the random number sequence showing:
   - Random number values over time
   - Pattern and distribution visualization

3. `distribution_plot.png`: Histogram showing:
   - Distribution of generated random numbers
   - Frequency analysis of values

4. `generated_numbers.txt`: Raw list of all random numbers used in the simulation

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
