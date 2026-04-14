"""Convertit benchmark.md en benchmark.json.

Usage :
    uv run python datasets/sfar_antibioprophylaxie/md_to_json.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_DIR = Path(__file__).parent
MD_PATH = _DIR / "benchmark.md"
JSON_PATH = _DIR / "benchmark.json"

# Métadonnées du dataset (alignées sur le schéma attendu par dataset_loader.py).
_DATASET_META = {
    "id": "sfar-antibioprophylaxie",
    "version": "1.0",
    "source": "RFE SFAR 2024 (V2.0 du 22/05/2024)",
    "scope": "Chirurgie orthopédique programmée + Traumatologie",
    "system_prompt": (
        "Tu es un expert en antibioprophylaxie chirurgicale. "
        "Réponds de façon concise :\n"
        "- Pour les questions ouvertes : réponds uniquement par le nom de la "
        "molécule (ex : 'Céfazoline', 'Amoxicilline/Clavulanate', 'Non', "
        "'Hors périmètre', etc.). Aucune explication.\n"
        "- Pour les questions à choix multiples : réponds uniquement par la "
        "lettre (A, B, C ou D). Aucune explication."
    ),
}

# Le Markdown utilise "qcm", le domaine attend "mcq".
_TYPE_MAP = {"qcm": "mcq"}


def parse_benchmark(text: str) -> list[dict]:
    """Parse le Markdown structuré et retourne une liste de questions."""
    questions: list[dict] = []
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)

    for block in blocks:
        if not block.strip():
            continue
        title_match = re.match(r"(Q\d+)\s*[—–-]\s*(.+)", block.split("\n")[0])
        if not title_match:
            continue

        qid = title_match.group(1)

        q: dict = {"id": qid}

        # Parser les champs "- **clé** : valeur" ([ \t] évite de traverser les \n)
        for match in re.finditer(r"^- \*\*(\w+(?:[- ]\w+)*)\*\*[ \t]*:[ \t]*(.+)$", block, re.MULTILINE):
            key = match.group(1).strip().replace(" ", "_").replace("-", "_")
            value = match.group(2).strip()
            q[key] = value

        # Normaliser le type (qcm → mcq)
        if "type" in q:
            q["type"] = _TYPE_MAP.get(q["type"], q["type"])

        # Parser les choix QCM (lignes "  - A. ...")
        choices_matches = re.findall(r"^\s+- ([A-Z])\.\s+(.+)$", block, re.MULTILINE)
        if choices_matches:
            q["choices"] = {letter: text.strip() for letter, text in choices_matches}

        if "réponse" in q:
            q["réponse"] = q["réponse"].strip()

        if q.get("type") or q.get("question"):
            questions.append(q)

    return questions


def main() -> None:
    if not MD_PATH.exists():
        print(f"Erreur : {MD_PATH} introuvable", file=sys.stderr)
        sys.exit(1)

    text = MD_PATH.read_text(encoding="utf-8")
    questions = parse_benchmark(text)

    output = {**_DATASET_META, "questions": questions}

    JSON_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(questions)} questions converties → {JSON_PATH}")


if __name__ == "__main__":
    main()
