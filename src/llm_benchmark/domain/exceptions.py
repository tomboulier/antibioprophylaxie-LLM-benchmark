"""Domain exceptions for llm-benchmark."""


class DatasetValidationError(Exception):
    """Raised when a dataset JSON file fails validation.

    Parameters
    ----------
    errors : list[str]
        Non-empty list of human-readable error messages describing each
        validation failure found in the dataset.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"Dataset validation failed with {len(errors)} error(s): {errors}")
