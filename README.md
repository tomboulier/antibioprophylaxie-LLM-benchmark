# Antibioprophylaxie LLM Benchmark

Benchmark scientifique pour évaluer différentes approches d'IA appliquées aux recommandations d'antibioprophylaxie chirurgicale (RFE SFAR 2024).

## Objectif

Comparer **5 systèmes** pour déterminer lequel est "meilleur" pour répondre aux questions d'antibioprophylaxie:

| Système | Description | Métrique clé |
|---------|-------------|--------------|
| **RAG Niveau 1** | Retrieval sur PDF | Temps + Précision |
| **RAG Niveau 2** | Retrieval sur Excel structuré | Coûts |
| **Long Context** | Tout le texte en Claude Opus | Latency |
| **MCP Server** | Model Context Protocol avec tools | Réponses sourcées |
| **LLM Fine-tuné** | Fine-tuning sur instruction set | Précision fine |

## Données

- **Dataset de test**: 25 questions avec réponses attendues (`research/benchmark.json`)
- **Source**: RFE SFAR 2024 (V2.0 du 22/05/2024)
- **Périmètre**: Chirurgie orthopédique + Traumatologie (47 interventions)
- **Auteur initial**: Claude (à valider/corriger par un MD)

## Usage

### 1. Setup

```bash
# Installer les dépendances
uv sync --extra dev

# Exporter les clés API
export ANTHROPIC_API_KEY=sk-...
export OPENAI_API_KEY=sk-...
export MISTRAL_API_KEY=...
```

### 2. Préparer les questions

Si vous éditez `research/benchmark.md`:

```bash
uv run python scripts/benchmark_md_to_json.py
```

### 3. Lancer le benchmark

```bash
# Un modèle
uv run python scripts/run_benchmark.py --model claude-sonnet

# Plusieurs modèles (comparaison)
uv run python scripts/run_benchmark.py -m claude-sonnet -m gpt-4o -m mistral-large

# Voir les modèles disponibles
uv run python scripts/run_benchmark.py --list-models
```

Résultats: `research/results/<model>_<timestamp>.json`

### 4. Analyser

```bash
# (À implémenter) 
uv run python scripts/eval_results.py --compare gpt-4o claude-sonnet
```

## Structure

```
research/
├── benchmark.md       ← Questions en Markdown (source de vérité)
├── benchmark.json     ← Questions compilées (généré)
└── results/           ← Résultats (JSON + CSV)

scripts/
├── benchmark_md_to_json.py     ← Parser
├── run_benchmark.py            ← Orchestrateur
└── eval_results.py             ← Analyseur (TBD)

docs/
├── s-019.md                    ← Story file
└── findings-report.md          ← Résultats finaux (TBD)
```

## Métriques

- **Précision**: % de réponses correctes
- **Latency**: Temps moyen par question (s)
- **Coûts**: Tokens ou calories consommés
- **Écologie**: Émissions CO2 estimées
- **Sourçage**: Réponses incluent citation/source?

## Résultats actuels

Aucun résultat encore. En cours de développement (S-019).

## Contributing

1. Fork ou branche `feat/xxx`
2. Éditer `research/benchmark.md` si besoin
3. Tester les scripts
4. Commit + PR

Voir [CONTRIBUTING.md](#) pour conventions.

## Lié à

- **App principale**: [recos-antibioprophylaxie-SFAR](https://github.com/tomboulier/recos-antibioprophylaxie-SFAR)
- **Déploiement app**: https://recos-antibioprophylaxie-sfar.onrender.com

## License

Voir LICENSE du repo principal (hérité).
