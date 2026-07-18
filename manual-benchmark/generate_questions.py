"""Génère questions.json (questions SANS réponses) depuis benchmark.json.

Cette version « questions seules » est la pièce jointe à fournir aux interfaces
de chat (ChatGPT, Mistral Le Chat, Claude, MedGPT…). On retire volontairement le
champ ``réponse`` (et pour les QCM la lettre correcte reste absente) afin de ne
pas divulguer la vérité terrain au modèle interrogé.

Usage :
    uv run python manual-benchmark/generate_questions.py
    # ou, sans uv :
    python manual-benchmark/generate_questions.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_DIR = Path(__file__).parent
BENCHMARK_PATH = _DIR.parent / "datasets" / "sfar_antibioprophylaxie" / "benchmark.json"
QUESTIONS_PATH = _DIR / "questions.json"

# Champs conservés dans la pièce jointe (ordre stable, blindé de toute réponse).
_KEEP = ("id", "type", "question", "choices")


def strip_answers(benchmark: dict) -> dict:
    """Retourne un dataset ne contenant que l'énoncé des questions.

    Parameters
    ----------
    benchmark : dict
        Contenu de ``benchmark.json`` (avec réponses).

    Returns
    -------
    dict
        Dataset « questions seules », prêt à être joint à un chat.
    """
    questions = []
    for q in benchmark["questions"]:
        clean = {k: q[k] for k in _KEEP if k in q}
        questions.append(clean)

    return {
        "id": benchmark.get("id"),
        "version": benchmark.get("version"),
        "source": benchmark.get("source"),
        "scope": benchmark.get("scope"),
        "question_count": len(questions),
        "questions": questions,
    }


def main() -> None:
    if not BENCHMARK_PATH.exists():
        print(f"Erreur : {BENCHMARK_PATH} introuvable", file=sys.stderr)
        sys.exit(1)

    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    output = strip_answers(benchmark)

    QUESTIONS_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{output['question_count']} questions (sans réponses) → {QUESTIONS_PATH}")


if __name__ == "__main__":
    main()
