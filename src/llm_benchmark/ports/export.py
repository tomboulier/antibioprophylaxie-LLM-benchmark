"""ExportPort — abstract interface for result serialisation adapters."""

from abc import ABC, abstractmethod
from pathlib import Path

from llm_benchmark.domain.entities import RunResult


class ExportPort(ABC):
    """Contract that every export adapter must fulfil.

    An export adapter serialises a ``RunResult`` to a specific format
    (JSON, CSV, etc.) and writes it to the given output directory.
    """

    @abstractmethod
    def export(self, result: RunResult, output_dir: Path) -> Path:
        """Serialise a run result and write it to disk.

        Parameters
        ----------
        result : RunResult
            The benchmark run result to serialise.
        output_dir : Path
            Directory where the output file should be written.

        Returns
        -------
        Path
            Absolute path to the file that was created.
        """
