class SimulationError(Exception):
    """Base class for exceptions in this simulation."""

    pass


class RandomNumberExhaustedError(SimulationError):
    """Raised when the random number generator runs out of numbers."""

    pass


class InvalidQueueConfigurationError(SimulationError):
    """Raised when a queue is configured incorrectly."""

    pass


class InvalidEventError(SimulationError):
    """Raised when an invalid event is encountered."""

    pass
