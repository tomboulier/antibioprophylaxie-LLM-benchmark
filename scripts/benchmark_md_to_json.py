"""Convertit research/benchmark.md en research/benchmark.json.

Usage :
    uv run python scripts/benchmark_md_to_json.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MD_PATH = Path("research/benchmark.md")
JSON_PATH = Path("research/benchmark.json")


def parse_benchmark(text: str) -> list[dict]:
    """Parse le Markdown structuré et retourne une liste de questions."""
    questions: list[dict] = []
    # Découper par question (### Qxx)
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)

    for block in blocks:
        if not block.strip():
            continue
        # Extraire l'ID depuis le titre (ex: "Q01 — Protocole standard PTH")
        title_match = re.match(r"(Q\d+)\s*[—–-]\s*(.+)", block.split("\n")[0])
        if not title_match:
            continue

        qid = title_match.group(1)
        title = title_match.group(2).strip()

        q: dict = {"id": qid, "titre": title}

        # Parser les champs "- **clé** : valeur"
        for match in re.finditer(
            r"^- \*\*(\w+(?:[- ]\w+)*)\*\*\s*:\s*(.+)$", block, re.MULTILINE
        ):
            key = match.group(1).strip().replace(" ", "_").replace("-", "_")
            value = match.group(2).strip()
            q[key] = value

        # Parser les choix QCM (lignes "  - A. ...")
        choix_matches = re.findall(
            r"^\s+- ([A-Z])\.\s+(.+)$", block, re.MULTILINE
        )
        if choix_matches:
            q["choix"] = {letter: text.strip() for letter, text in choix_matches}

        # Convertir la difficulté telle quelle, nettoyer la réponse
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

    output = {
        "version": "1.0",
        "source": "RFE SFAR 2024 (V2.0 du 22/05/2024)",
        "perimetre": "Chirurgie orthopédique programmée + Traumatologie",
        "nb_questions": len(questions),
        "questions": questions,
    }

    JSON_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(questions)} questions converties → {JSON_PATH}")


if __name__ == "__main__":
    main()
