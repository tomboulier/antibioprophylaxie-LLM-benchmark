"""Convertit benchmark.json en benchmark.md.

Round-trip inverse de md_to_json.py.

Usage :
    uv run python datasets/sfar_antibioprophylaxie/json_to_md.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_DIR = Path(__file__).parent
JSON_PATH = _DIR / "benchmark.json"
MD_PATH = _DIR / "benchmark.md"

HEADER = """\
# Benchmark Antibioprophylaxie SFAR

> Jeu de questions standardisé pour évaluer tout système (RAG, MCP, chatbot, LLM)
> sur les recommandations d'antibioprophylaxie chirurgicale (RFE SFAR 2024).
>
> **Source** : {source}
> **Auteur initial** : Claude (à valider/corriger par un médecin)
> **Date** : 2026-03-11

## Format des réponses attendues

Pour les questions ouvertes, la réponse attendue est :
- Un **nom de molécule** (ex : `Céfazoline`)
- Ou bien `Non` (pas d'antibioprophylaxie recommandée)

Pour les QCM, une seule réponse correcte (lettre).

---
"""

# Le domaine stocke "mcq", le Markdown affiche "qcm".
_TYPE_MAP_REVERSE = {"mcq": "qcm"}


def question_to_md(q: dict) -> str:
    """Convertit une question (dict) en bloc Markdown."""
    qid = q["id"]
    titre = q.get("titre", q["question"][:50])
    md_type = _TYPE_MAP_REVERSE.get(q["type"], q["type"])

    lines = [f"### {qid} -- {titre}", ""]

    lines.append(f"- **type** : {md_type}")
    lines.append(f"- **question** : {q['question']}")

    if q["type"] in ("qcm", "mcq") and "choices" in q:
        lines.append("- **choix** :")
        for letter, text in sorted(q["choices"].items()):
            lines.append(f"  - {letter}. {text}")

    lines.append(f"- **réponse** : {q['réponse']}")

    if "source" in q:
        lines.append(f"- **source** : {q['source']}")

    return "\n".join(lines)


def main() -> None:
    if not JSON_PATH.exists():
        print(f"Erreur : {JSON_PATH} introuvable", file=sys.stderr)
        sys.exit(1)

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    questions = data["questions"]

    open_qs = [q for q in questions if q["type"] == "open"]
    mcq_qs = [q for q in questions if q["type"] == "mcq"]

    parts = [HEADER.format(source=data.get("source", "RFE SFAR 2024"))]

    if open_qs:
        parts.append("## Questions ouvertes")
        parts.append("")
        for q in open_qs:
            parts.append(question_to_md(q))
            parts.append("")

    if mcq_qs:
        parts.append("---")
        parts.append("")
        parts.append("## QCM")
        parts.append("")
        for q in mcq_qs:
            parts.append(question_to_md(q))
            parts.append("")

    MD_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"{len(questions)} questions converties → {MD_PATH}")


if __name__ == "__main__":
    main()
