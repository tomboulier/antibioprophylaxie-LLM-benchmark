"""CarbonTrackerPort — abstract interface for carbon emission tracking adapters."""

from abc import ABC, abstractmethod

from llm_benchmark.domain.value_objects import CarbonFootprint


class CarbonTrackerPort(ABC):
    """Contract for carbon emission tracking adapters.

    Implementations wrap external tools (e.g. CodeCarbon) and translate
    their output into the domain's ``CarbonFootprint`` value object.
    """

    @abstractmethod
    def start(self) -> None:
        """Start tracking emissions for the current run.

        Returns
        -------
        None
        """

    @abstractmethod
    def stop(self) -> CarbonFootprint:
        """Stop tracking and return the measured carbon footprint.

        Returns
        -------
        CarbonFootprint
            Estimated CO2 equivalent in grams for the tracked period.
        """
