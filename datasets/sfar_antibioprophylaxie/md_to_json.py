"""Convertit benchmark.md en benchmark.json.

Usage CLI :
    uv run python datasets/sfar_antibioprophylaxie/md_to_json.py

Import :
    from <module> import generate  # ou via importlib
    count = generate(md_path, json_path)
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
        "molécule (ex : 'Céfazoline', 'Amoxicilline/Clavulanate'), "
        "par 'Pas d'antibioprophylaxie', ou par 'Hors périmètre' si la "
        "situation n'est pas couverte par les recommandations. "
        "Aucune explication.\n"
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
    seq = 0

    for block in blocks:
        if not block.strip():
            continue
        first_line = block.split("\n")[0].strip()
        if not first_line:
            continue

        # Ignorer les lignes sans champ structuré (sections, etc.)
        has_fields = re.search(r"^- \*\*\w+", block, re.MULTILINE)
        if not has_fields:
            continue

        seq += 1
        titre = first_line
        qid = f"Q{seq:02d}"

        q: dict = {"id": qid, "titre": titre}

        # Parser les champs "- **clé** : valeur" ([ \t] évite de traverser les \n)
        for match in re.finditer(
            r"^- \*\*(\w+(?:[- ]\w+)*)\*\*[ \t]*:[ \t]*(.+)$", block, re.MULTILINE
        ):
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


def generate(md_path: Path = MD_PATH, json_path: Path = JSON_PATH) -> int:
    """Convertit le Markdown en JSON et écrit le fichier cible.

    Parameters
    ----------
    md_path : Path
        Chemin du fichier Markdown source.
    json_path : Path
        Chemin du fichier JSON à écrire.

    Returns
    -------
    int
        Nombre de questions converties.

    Raises
    ------
    FileNotFoundError
        Si ``md_path`` n'existe pas.
    """
    if not md_path.exists():
        raise FileNotFoundError(md_path)

    text = md_path.read_text(encoding="utf-8")
    questions = parse_benchmark(text)

    output = {**_DATASET_META, "questions": questions}

    json_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(questions)


def main() -> None:
    try:
        count = generate()
    except FileNotFoundError as err:
        print(f"Erreur : {err} introuvable", file=sys.stderr)
        sys.exit(1)
    print(f"{count} questions converties → {JSON_PATH}")


if __name__ == "__main__":
    main()
