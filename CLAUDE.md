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
uv run python datasets/sfar_antibioprophylaxie/md_to_json.py  # Convertir MD → JSON
uv run python datasets/sfar_antibioprophylaxie/json_to_md.py  # Convertir JSON → MD
uv run llm-benchmark run                       # Lancer le pipeline complet (modèles activés)
uv run llm-benchmark run -m gpt-4o             # Lancer sur un modèle spécifique
uv run llm-benchmark list models               # Lister les modèles disponibles
uv run pytest                 # Tests
uv run ruff check .           # Lint
uv run ruff format .          # Format
```

## Structure

```
src/llm_benchmark/
  cli/main.py                 ← Point d'entrée CLI (controller)
  usecases/run_experiment.py  ← Use case : pipeline complet
  domain/                     ← Entités, engine, scorer
  adapters/                   ← LLM (LiteLLM), exports (JSON, figures)
  ports/                      ← Interfaces abstraites

config/
  models.yaml                 ← Registry des modèles (enabled: true/false)

datasets/sfar_antibioprophylaxie/
  benchmark.md                ← Questions (source de vérité humaine)
  benchmark.json              ← Questions compilées (généré)
  md_to_json.py               ← Convertir MD → JSON
  json_to_md.py               ← Convertir JSON → MD

research/
  results/                    ← Résultats JSON par run
  figures/                    ← Figures PNG générées automatiquement
```

## Workflow

1. **Éditer** `datasets/sfar_antibioprophylaxie/benchmark.md` (ajouter/corriger questions)
2. **Compiler** : `uv run python datasets/sfar_antibioprophylaxie/md_to_json.py`
3. **Lancer** : `uv run llm-benchmark run` (pipeline complet automatisé)
4. **Résultats** : JSON dans `research/results/`, figures dans `research/figures/`
5. **Reporter** : générer findings report → `docs/findings-report.md`

## Ne pas faire

- Ne pas ajouter de dépendances sans justification
- Ne pas commiter de clés API ou secrets (.env)
- Ne pas sur-architecturer (pas d'interface abstraites)
- Ne pas modifier ce dépôt sans passer par une branche feature

## Lié à

- **Main app**: https://github.com/tomboulier/recos-antibioprophylaxie-SFAR
- **App docs**: Voir `docs/` du repo principal pour contexte domaine
