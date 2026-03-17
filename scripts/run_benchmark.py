"""Benchmark des modèles LLM sur les questions d'antibioprophylaxie.

Envoie les questions de research/benchmark.json à un ou plusieurs modèles,
collecte les réponses, évalue automatiquement, et sauvegarde les résultats.

Usage :
    # Un seul modèle
    uv run python scripts/run_benchmark.py --model claude-sonnet

    # Plusieurs modèles (comparaison)
    uv run python scripts/run_benchmark.py -m claude-sonnet -m gpt-4o -m mistral-large

    # Voir les modèles disponibles
    uv run python scripts/run_benchmark.py --list-models

Les clés API sont lues depuis les variables d'environnement :
    ANTHROPIC_API_KEY, OPENAI_API_KEY, MISTRAL_API_KEY

Résultats sauvegardés dans research/results/<model>_<timestamp>.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

BENCHMARK_PATH = Path("research/benchmark.json")
RESULTS_DIR = Path("research/results")

# --- Modèles disponibles ---

MODELS = {
    # Anthropic
    "claude-sonnet": ("anthropic", "claude-sonnet-4-20250514"),
    "claude-haiku": ("anthropic", "claude-haiku-4-5-20251001"),
    "claude-opus": ("anthropic", "claude-opus-4-20250514"),
    # OpenAI
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gpt-4.1": ("openai", "gpt-4.1"),
    "gpt-4.1-mini": ("openai", "gpt-4.1-mini"),
    "o3-mini": ("openai", "o3-mini"),
    # Mistral
    "mistral-large": ("mistral", "mistral-large-latest"),
    "mistral-small": ("mistral", "mistral-small-latest"),
}

SYSTEM_PROMPT = """\
Tu es un assistant médical spécialisé en antibioprophylaxie chirurgicale.
Tu réponds UNIQUEMENT sur la base des recommandations RFE SFAR 2024.

Pour les questions ouvertes, réponds par :
- Le nom de la molécule (ex: "Céfazoline"), ou plusieurs séparées par " + " si association (ex: "Clindamycine + Gentamicine")
- "Non" si pas d'antibioprophylaxie recommandée

Pour les QCM, réponds UNIQUEMENT par la lettre (A, B, C ou D), rien d'autre.

Un seul mot ou une seule lettre. Pas d'explication."""


def query_anthropic(model_id: str, question: str) -> str:
    """Interroge un modèle Anthropic."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model_id,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


def query_openai(model_id: str, question: str) -> str:
    """Interroge un modèle OpenAI."""
    import openai

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model_id,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content.strip()


def query_mistral(model_id: str, question: str) -> str:
    """Interroge un modèle Mistral."""
    from mistralai import Mistral

    client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", ""))
    response = client.chat.complete(
        model=model_id,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content.strip()


PROVIDERS = {
    "anthropic": query_anthropic,
    "openai": query_openai,
    "mistral": query_mistral,
}


def format_question(q: dict) -> str:
    """Formatte une question pour l'envoi au modèle."""
    text = q["question"]
    if q.get("type") == "qcm" and q.get("choix"):
        choices = "\n".join(f"{k}. {v}" for k, v in q["choix"].items())
        text += f"\n\n{choices}"
    return text


def score_qcm(expected: str, actual: str) -> dict:
    """Évalue une réponse QCM."""
    # Extraire la lettre de la réponse
    expected_letter = expected.strip().upper()
    # Chercher une lettre A-D dans la réponse
    match = re.search(r"\b([A-D])\b", actual.upper())
    actual_letter = match.group(1) if match else actual.strip().upper()[:1]

    correct = expected_letter == actual_letter
    return {
        "correct": correct,
        "expected_letter": expected_letter,
        "actual_letter": actual_letter,
    }


def normalize(text: str) -> str:
    """Normalise un texte pour la comparaison."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    # Retirer la ponctuation finale
    text = text.rstrip(".")
    return text


def score_open(expected: str, actual: str) -> dict:
    """Évalue une réponse ouverte (nom de molécule, Non, ou Hors périmètre)."""
    norm_expected = normalize(expected)
    norm_actual = normalize(actual)

    # "Non" → chercher "non" ou "pas d'antibioprophylaxie" dans la réponse
    if norm_expected == "non":
        correct = "non" in norm_actual or "pas d'" in norm_actual
        return {"correct": correct}

    # Nom de molécule(s) : vérifier que chaque molécule attendue est présente
    molecules = [m.strip() for m in expected.split("+")]
    found = all(normalize(m) in norm_actual for m in molecules)
    return {"correct": found}


def run_model(model_name: str, questions: list[dict]) -> dict:
    """Exécute le benchmark pour un modèle donné."""
    provider, model_id = MODELS[model_name]
    query_fn = PROVIDERS[provider]

    results = []
    correct_count = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"  Modèle : {model_name} ({model_id})")
    print(f"  {len(questions)} questions")
    print(f"{'='*60}\n")

    for i, q in enumerate(questions, 1):
        qid = q["id"]
        qtype = q.get("type", "open")
        prompt = format_question(q)

        print(f"  [{i:2d}/{len(questions)}] {qid} ({qtype})...", end=" ", flush=True)

        try:
            t0 = time.time()
            answer = query_fn(model_id, prompt)
            elapsed = time.time() - t0

            if qtype == "qcm":
                evaluation = score_qcm(q["réponse"], answer)
            else:
                evaluation = score_open(q["réponse"], answer)

            correct = evaluation["correct"]
            if correct:
                correct_count += 1
                print(f"OK ({elapsed:.1f}s)")
            else:
                print(f"FAIL ({elapsed:.1f}s)")
                print(f"         attendu : {q['réponse']}")
                print(f"         reçu    : {answer[:100]}")

            results.append({
                "id": qid,
                "type": qtype,
                "question": q["question"],
                "expected": q["réponse"],
                "actual": answer,
                "correct": correct,
                "time_s": round(elapsed, 2),
            })

        except Exception as e:
            errors += 1
            print(f"ERREUR : {e}")
            results.append({
                "id": qid,
                "type": qtype,
                "question": q["question"],
                "expected": q["réponse"],
                "actual": None,
                "correct": False,
                "error": str(e),
            })

    n = len(questions)
    accuracy = correct_count / n if n > 0 else 0

    print(f"\n  Résultats : {correct_count}/{n} ({accuracy:.0%})")
    if errors:
        print(f"  Erreurs : {errors}")

    return {
        "model_name": model_name,
        "model_id": model_id,
        "provider": provider,
        "timestamp": datetime.now(UTC).isoformat(),
        "summary": {
            "total": n,
            "correct": correct_count,
            "accuracy": round(accuracy, 4),
            "errors": errors,
            "by_type": _group_stats(results, "type"),
        },
        "results": results,
    }


def _group_stats(results: list[dict], key: str) -> dict:
    """Statistiques groupées par un champ des résultats."""
    groups: dict[str, dict] = {}
    for r in results:
        g = r.get(key, "?")
        if g not in groups:
            groups[g] = {"total": 0, "correct": 0}
        groups[g]["total"] += 1
        if r["correct"]:
            groups[g]["correct"] += 1
    for g in groups:
        n = groups[g]["total"]
        groups[g]["accuracy"] = round(groups[g]["correct"] / n, 4) if n else 0
    return groups



def save_results(run_data: dict) -> Path:
    """Sauvegarde les résultats dans research/results/."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    name = run_data["model_name"].replace("/", "-")
    path = RESULTS_DIR / f"{name}_{ts}.json"
    path.write_text(
        json.dumps(run_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n  Résultats sauvegardés : {path}")
    return path


def print_comparison(all_runs: list[dict]) -> None:
    """Affiche un tableau comparatif des modèles."""
    if len(all_runs) < 2:
        return

    print(f"\n{'='*60}")
    print("  COMPARAISON DES MODÈLES")
    print(f"{'='*60}\n")

    # Header
    header = f"  {'Modèle':<20} {'Correct':>8} {'Accuracy':>10}"
    print(header)
    print(f"  {'-'*40}")

    for run in sorted(all_runs, key=lambda r: r["summary"]["accuracy"], reverse=True):
        s = run["summary"]
        print(f"  {run['model_name']:<20} {s['correct']:>4}/{s['total']:<3} {s['accuracy']:>9.0%}")

    # Par type
    print("\n  Par type :")
    for qtype in ("open", "qcm"):
        print(f"    {qtype.upper():<6}", end="  ")
        for run in all_runs:
            stats = run["summary"]["by_type"].get(qtype, {})
            acc = stats.get("accuracy", 0)
            print(f"{run['model_name']}: {acc:.0%}", end="  ")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark des modèles LLM sur l'antibioprophylaxie SFAR"
    )
    parser.add_argument(
        "--model", "-m",
        action="append",
        dest="models",
        help=f"Modèle(s) à tester. Disponibles : {', '.join(sorted(MODELS))}",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Afficher les modèles disponibles",
    )
    parser.add_argument(
        "--questions", "-q",
        type=str,
        default=None,
        help="Filtrer par IDs de questions (ex: Q01,Q05,Q16)",
    )
    args = parser.parse_args()

    if args.list_models:
        print("\nModèles disponibles :\n")
        for name, (provider, model_id) in sorted(MODELS.items()):
            print(f"  {name:<20} {provider:<10} {model_id}")
        print("\nUsage : uv run python scripts/run_benchmark.py -m claude-sonnet -m gpt-4o\n")
        sys.exit(0)

    if not args.models:
        parser.error("Au moins un --model est requis (ou --list-models)")

    # Valider les modèles
    for m in args.models:
        if m not in MODELS:
            parser.error(f"Modèle inconnu : {m}. Voir --list-models")

    # Charger le benchmark
    if not BENCHMARK_PATH.exists():
        print(f"Erreur : {BENCHMARK_PATH} introuvable", file=sys.stderr)
        print("Lancez d'abord : uv run python scripts/benchmark_md_to_json.py", file=sys.stderr)
        sys.exit(1)

    data = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    questions = data["questions"]

    # Filtrer si demandé
    if args.questions:
        ids = {qid.strip() for qid in args.questions.split(",")}
        questions = [q for q in questions if q["id"] in ids]
        if not questions:
            print(f"Aucune question trouvée pour : {args.questions}", file=sys.stderr)
            sys.exit(1)

    print("\nBenchmark Antibioprophylaxie SFAR")
    print(f"Source : {data.get('source', '?')}")
    print(f"Questions : {len(questions)}")
    print(f"Modèles : {', '.join(args.models)}")

    # Exécuter
    all_runs = []
    for model_name in args.models:
        run_data = run_model(model_name, questions)
        save_results(run_data)
        all_runs.append(run_data)

    print_comparison(all_runs)


if __name__ == "__main__":
    main()
