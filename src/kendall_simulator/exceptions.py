# kendall-simulator/src/exceptions.py
"""
Custom exceptions for the Kendall Queue Network Simulator.

This module defines a set of custom exceptions used throughout the simulator
to handle various error conditions specific to queue network simulation.
"""


class SimulationError(Exception):
    """Base class for exceptions in this simulation."""


class InvalidQueueConfigurationError(SimulationError):
    """Raised when a queue is configured incorrectly."""


class InvalidEventError(SimulationError):
    """Raised when an invalid event is encountered."""


class OutOfRandomNumbersError(SimulationError):
    """Raised when the random number generator runs out of numbers."""
