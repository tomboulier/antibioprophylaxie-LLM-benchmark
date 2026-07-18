"""Génère les pièces jointes « questions seules » depuis benchmark.json.

Produit deux fichiers synchronisés, à joindre aux interfaces de chat (ChatGPT,
Mistral Le Chat, Claude, MedGPT…) :

- ``questions.json`` : format structuré (défaut) ;
- ``questions.md`` : variante **texte brut** (liste numérotée) pour les outils
  qui refusent le JSON ou les pièces jointes (ex. MedGPT), à coller directement.

On retire volontairement le champ ``réponse`` (et pour les QCM la lettre
correcte reste absente) afin de ne pas divulguer la vérité terrain.

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
QUESTIONS_MD_PATH = _DIR / "questions.md"

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


def to_markdown(dataset: dict) -> str:
    """Rend le dataset « questions seules » en Markdown texte brut.

    Parameters
    ----------
    dataset : dict
        Sortie de :func:`strip_answers`.

    Returns
    -------
    str
        Liste numérotée des questions (énoncés + choix QCM), sans réponse.
    """
    lines = [
        f"# Questions — {dataset.get('id')} (dataset v{dataset.get('version')})",
        "",
        f"{dataset['question_count']} questions. Les réponses ne sont "
        "volontairement pas fournies (c'est un test).",
        "",
    ]
    for q in dataset["questions"]:
        kind = "QCM" if q.get("type") == "mcq" else "ouverte"
        lines.append(f"## {q['id']} ({kind})")
        lines.append(q["question"])
        for letter, text in (q.get("choices") or {}).items():
            lines.append(f"- {letter}. {text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


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
    QUESTIONS_MD_PATH.write_text(to_markdown(output), encoding="utf-8")
    n = output["question_count"]
    print(f"{n} questions (sans réponses) → {QUESTIONS_PATH}")
    print(f"{n} questions (texte brut)   → {QUESTIONS_MD_PATH}")


if __name__ == "__main__":
    main()
