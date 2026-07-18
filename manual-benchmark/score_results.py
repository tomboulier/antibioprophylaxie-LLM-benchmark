"""Scorer hors-ligne pour les résultats collectés manuellement.

Compare un ou plusieurs fichiers de résultats (au format renvoyé par le prompt,
voir ``prompts/``) à la vérité terrain de ``benchmark.json``, puis affiche un
comparatif de précision (global + par type de question).

La logique de notation est **identique** à celle du pipeline automatisé
(``src/llm_benchmark/domain/scorer.py``) afin que les deux approches soient
directement comparables. Le score global porte sur les questions **répondues** ;
le nombre de questions manquantes est affiché à part (colonne « Manquantes »).

Usage :
    python manual-benchmark/score_results.py manual-benchmark/results/*.json
    # ou un fichier précis :
    python manual-benchmark/score_results.py manual-benchmark/results/claude.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_DIR = Path(__file__).parent
BENCHMARK_PATH = _DIR.parent / "datasets" / "sfar_antibioprophylaxie" / "benchmark.json"


def normalize(text: str) -> str:
    """Normalise un texte pour comparaison (identique au pipeline).

    Minuscule, trim, espaces multiples réduits, point final retiré. Les accents
    ne sont **pas** retirés (``Cefazoline`` ne matche donc pas ``Céfazoline``).

    Parameters
    ----------
    text : str
        Texte brut à normaliser.

    Returns
    -------
    str
        Texte normalisé.
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".").strip()
    return text


def score_open(expected: str, actual: str) -> bool:
    """Note une question ouverte (cf. OpenScorer du domaine).

    Parameters
    ----------
    expected : str
        Réponse attendue (nom de molécule(s), ``Pas d'antibioprophylaxie`` ou
        ``Hors périmètre``).
    actual : str
        Réponse fournie par l'outil.

    Returns
    -------
    bool
        ``True`` si la réponse est jugée correcte.
    """
    normalized_expected = normalize(expected)
    normalized_actual = normalize(actual)
    if normalized_expected in ("pas d'antibioprophylaxie", "hors périmètre"):
        return normalized_expected in normalized_actual
    molecules = [normalize(m) for m in expected.split("+")]
    return all(m in normalized_actual for m in molecules)


def score_mcq(expected: str, actual: str) -> bool:
    """Note une question à choix multiples (cf. QCMScorer du domaine).

    Parameters
    ----------
    expected : str
        Lettre attendue (``A``–``D``).
    actual : str
        Réponse fournie ; la première lettre ``A``–``D`` trouvée est comparée.

    Returns
    -------
    bool
        ``True`` si la lettre extraite correspond à la lettre attendue.
    """
    expected_letter = expected.strip().upper()
    match = re.search(r"\b([A-D])\b", actual.upper())
    return (match.group(1) if match else None) == expected_letter


def load_benchmark() -> dict:
    """Charge le benchmark et l'indexe par id de question.

    Returns
    -------
    dict
        Dictionnaire ``{id: question}`` (chaque question porte sa ``réponse``).
    """
    data = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    return {q["id"]: q for q in data["questions"]}


def score_file(path: Path, benchmark: dict) -> dict:
    """Score un fichier de résultats et retourne un récapitulatif.

    Parameters
    ----------
    path : Path
        Fichier JSON au format de sortie du prompt.
    benchmark : dict
        Questions indexées par id (avec réponses attendues).

    Returns
    -------
    dict
        Récapitulatif avec les clés : ``model``, ``mode`` et ``prompt_version``
        (champs de traçabilité, ``"?"`` si absents), ``totals`` (compteurs
        ``[corrects, total]`` pour ``all``/``open``/``mcq``), ``errors`` (liste
        des réponses fausses) et ``missing`` (ids sans réponse).
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    model = payload.get("modele") or path.stem
    # Champs de traçabilité (schéma v2 ; absents des runs v1 → "?").
    mode = payload.get("mode", "?")
    prompt_version = payload.get("prompt_version", "?")
    answers = {r["id"]: r["reponse"] for r in payload.get("reponses", [])}

    totals = {"all": [0, 0], "open": [0, 0], "mcq": [0, 0]}  # [correct, total]
    errors: list[dict] = []
    missing: list[str] = []

    for qid, q in benchmark.items():
        qtype = q["type"]
        if qid not in answers:
            missing.append(qid)
            continue
        actual = str(answers[qid])
        expected = q["réponse"]
        ok = score_mcq(expected, actual) if qtype == "mcq" else score_open(expected, actual)

        totals["all"][1] += 1
        totals[qtype][1] += 1
        if ok:
            totals["all"][0] += 1
            totals[qtype][0] += 1
        else:
            errors.append({"id": qid, "attendu": expected, "obtenu": actual})

    return {
        "model": model,
        "mode": mode,
        "prompt_version": prompt_version,
        "totals": totals,
        "errors": errors,
        "missing": missing,
    }


def pct(correct: int, total: int) -> str:
    """Formate un pourcentage lisible.

    Parameters
    ----------
    correct : int
        Nombre de réponses correctes.
    total : int
        Nombre de réponses évaluées.

    Returns
    -------
    str
        Pourcentage formaté (``'  n/a'`` si ``total`` vaut 0).
    """
    return f"{100 * correct / total:5.1f}%" if total else "  n/a"


def main(argv: list[str]) -> int:
    """Point d'entrée CLI : score les fichiers passés en arguments.

    Chaque fichier est scoré indépendamment ; un fichier illisible ou invalide
    est signalé sur ``stderr`` et ignoré, sans interrompre les autres.

    Parameters
    ----------
    argv : list[str]
        Chemins des fichiers de résultats à scorer.

    Returns
    -------
    int
        Code de sortie (0 = succès, 1 = aucun fichier valide / erreur).
    """
    if not argv:
        print(__doc__)
        return 1
    if not BENCHMARK_PATH.exists():
        print(f"Erreur : {BENCHMARK_PATH} introuvable", file=sys.stderr)
        return 1

    benchmark = load_benchmark()
    summaries = []
    for arg in argv:
        try:
            summaries.append(score_file(Path(arg), benchmark))
        except (OSError, ValueError, KeyError) as exc:
            print(f"⚠ {arg} ignoré ({type(exc).__name__} : {exc})", file=sys.stderr)
    if not summaries:
        print("Aucun fichier valide à scorer.", file=sys.stderr)
        return 1

    # Tableau comparatif
    header = (
        f"{'Modèle':<26} {'Mode':>4} {'Prompt':>7} "
        f"{'Global':>8} {'Open':>8} {'QCM':>8} {'Manquantes':>11}"
    )
    print(header)
    print("-" * len(header))
    for s in sorted(summaries, key=lambda x: -x["totals"]["all"][0]):
        t = s["totals"]
        print(
            f"{s['model']:<26} {s['mode']:>4} {s['prompt_version']:>7} "
            f"{pct(*t['all']):>8} {pct(*t['open']):>8} {pct(*t['mcq']):>8} "
            f"{len(s['missing']):>11}"
        )

    # Détail des erreurs par modèle
    for s in summaries:
        if s["errors"] or s["missing"]:
            print(
                f"\n### {s['model']} — {len(s['errors'])} erreur(s), "
                f"{len(s['missing'])} manquante(s)"
            )
            for e in s["errors"]:
                print(f"  {e['id']}: attendu «{e['attendu']}» / obtenu «{e['obtenu']}»")
            if s["missing"]:
                print(f"  Manquantes : {', '.join(s['missing'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
