# CLAUDE.md — Instructions pour Claude Code

## Contexte du projet

Benchmark scientifique comparant **5 approches d'IA** pour répondre aux questions d'antibioprophylaxie chirurgicale (RFE SFAR 2024):

1. **RAG niveau 1** (PDF) — Retrieval sur le PDF original
2. **RAG niveau 2** (Excel) — Retrieval sur l'export structuré
3. **Long context** (Claude) — Tout le texte en context window
4. **Serveur MCP** — Model Context Protocol avec tools
5. **LLM fine-tuné** — Fine-tuning sur instruction set

## Objectifs (S-019)

- **Questions de test** : Dataset de ~25 questions standardisées avec réponses attendues
- **Scripts d'évaluation** : Interroger chaque système, scorer automatiquement (précision, latency, coûts)
- **Résultats** : Comparatif clair (précision %, temps réponse, tokens consommés, émissions)
- **Findings report** : Recommandation finale pour l'intégration dans l'app SFAR

## Stack

- **Python 3.12** — Langage principal
- **Gestionnaire**: `uv` (pas pip)
- **Clients LLM**: `anthropic`, `openai`, `mistral` (conditionnels)
- **Linter/formatter**: `ruff`

## Conventions

- Conventional commits: `type(scope): description en français`
- TDD: Tests avant code (coverage >= 80% pour logique métier)
- Docstrings **numpydoc** sur fonctions publiques
- KISS, YAGNI — Pas de sur-architecture

## Commandes essentielles

```bash
uv sync --extra dev           # Installer dépendances
uv run python scripts/benchmark_md_to_json.py  # Convertir MD → JSON
uv run python scripts/benchmark_json_to_md.py  # Convertir JSON → MD (round-trip)
uv run python scripts/run_benchmark.py --model claude-sonnet  # Lancer benchmark
uv run pytest                 # Tests
uv run ruff check .           # Lint
uv run ruff format .          # Format
```

## Structure

```
research/
  benchmark.md      ← Questions en Markdown léger (source de vérité humaine)
  benchmark.json    ← Questions compilées (source de vérité machine, généré)
  results/          ← Résultats d'exécution (JSON + CSV)

scripts/
  benchmark_md_to_json.py     ← Parser MD → JSON
  benchmark_json_to_md.py     ← Parser JSON → MD (round-trip)
  run_benchmark.py            ← Orchestrer les requêtes & scoring
  (à ajouter) eval_results.py ← Analyser & générer rapport

docs/                         ← Documentation du recherche
  s-019.md                    ← Story file avec spec complète
  findings-report.md          ← Résultats & recommandations (final)
```

## Workflow

1. **Éditer** `research/benchmark.md` (ajouter/corriger questions)
2. **Compiler** : `uv run python scripts/benchmark_md_to_json.py`
3. **Lancer** : `uv run python scripts/run_benchmark.py -m claude-sonnet -m gpt-4o`
4. **Analyser** : résultats stockés dans `research/results/`
5. **Reporter** : générer findings report → `docs/findings-report.md`

## Ne pas faire

- Ne pas ajouter de dépendances sans justification
- Ne pas commiter de clés API ou secrets (.env)
- Ne pas sur-architecturer (pas d'interface abstraites)
- Ne pas modifier ce dépôt sans passer par une branche feature

## Lié à

- **Main app**: https://github.com/tomboulier/recos-antibioprophylaxie-SFAR
- **App docs**: Voir `docs/` du repo principal pour contexte domaine
