"""Value Objects du domaine llm-benchmark.

Objets valeur immuables (frozen dataclasses) avec validation des invariants.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Cost:
    """Coût monétaire avec devise explicite."""

    amount: float
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Cost cannot be negative: {self.amount}")
        if self.currency not in ("USD", "EUR"):
            raise ValueError(f"Unsupported currency: {self.currency}")


@dataclass(frozen=True)
class Latency:
    """Latence en secondes."""

    seconds: float

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise ValueError(f"Latency cannot be negative: {self.seconds}")


@dataclass(frozen=True)
class CarbonFootprint:
    """Empreinte carbone en grammes de CO2 équivalent."""

    g_co2e: float

    def __post_init__(self) -> None:
        if self.g_co2e < 0:
            raise ValueError(f"Carbon footprint cannot be negative: {self.g_co2e}")


@dataclass(frozen=True)
class Accuracy:
    """Précision entre 0.0 et 1.0."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Accuracy must be between 0 and 1: {self.value}")

    @property
    def as_percent(self) -> float:
        """Retourne la précision en pourcentage."""
        return self.value * 100


@dataclass(frozen=True)
class ModelId:
    """Identifiant d'un grand modèle de langage."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ModelId cannot be empty")


@dataclass(frozen=True)
class ApproachId:
    """Identifiant d'une approche."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ApproachId cannot be empty")


@dataclass(frozen=True)
class DatasetId:
    """Identifiant d'un jeu de données."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("DatasetId cannot be empty")


@dataclass(frozen=True)
class RunId:
    """Identifiant unique d'une exécution (UUID)."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("RunId cannot be empty")


@dataclass(frozen=True)
class QuestionId:
    """Identifiant d'une question dans un jeu de données."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("QuestionId cannot be empty")


@dataclass(frozen=True)
class DatasetVersion:
    """Version d'un jeu de données."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("DatasetVersion cannot be empty")


@dataclass(frozen=True)
class Source:
    """Référence bibliographique ou identifiant de source."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Source cannot be empty")


@dataclass(frozen=True)
class MCQChoices:
    """Choix de réponse pour une question QCM (clés A–D).

    Note: dict n'est pas hashable, donc __hash__ est désactivé
    (unsafe_hash=False implicite avec frozen=True + champ mutable).
    On override __hash__ pour utiliser les items triés.
    """

    choices: dict

    def __post_init__(self) -> None:
        valid_keys = {"A", "B", "C", "D"}
        if not self.choices:
            raise ValueError("MCQChoices cannot be empty")
        invalid = set(self.choices.keys()) - valid_keys
        if invalid:
            raise ValueError(f"Invalid MCQ keys: {invalid}")

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.choices.items())))


class QuestionType(Enum):
    """Type d'une question dans un jeu de données."""

    OPEN = "open"
    MCQ = "mcq"
