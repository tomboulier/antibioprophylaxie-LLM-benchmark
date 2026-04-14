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

- **Dataset de test**: 24 questions avec réponses attendues (`datasets/sfar_antibioprophylaxie/benchmark.json`)
- **Source**: RFE SFAR 2024 (V2.0 du 22/05/2024)
- **Périmètre**: Chirurgie orthopédique + Traumatologie (47 interventions)
- **Auteur initial**: Claude (à valider/corriger par un MD)

## Usage

### 1. Setup

```bash
# Installer les dépendances (dev + clients LLM)
uv sync --extra dev --extra llm

# Configurer les clés API
cp .env.example .env
# Éditer .env et remplacer les valeurs par vos vraies clés API
```

> **Note:** Les variables d'environnement déjà exportées dans le shell ont la priorité sur les valeurs définies dans `.env` (comportement non-override).

### 2. Préparer les questions

Si vous éditez `datasets/sfar_antibioprophylaxie/benchmark.md` :

```bash
uv run python datasets/sfar_antibioprophylaxie/md_to_json.py
```

### 3. Lancer le benchmark

```bash
# Pipeline complet (tous les modèles activés, résultats + figures)
uv run llm-benchmark run

# Modèle(s) spécifique(s)
uv run llm-benchmark run -m gpt-4o -m mistral-small-latest

# Questions spécifiques
uv run llm-benchmark run -q Q01,Q05,Q16

# Voir les modèles disponibles
uv run llm-benchmark list models
```

Résultats : `research/results/` (JSON) et `research/figures/` (PNG).

Les modèles activés par défaut se configurent dans `config/models.yaml` (champ `enabled`).

## Structure

```
src/llm_benchmark/
├── cli/main.py                 ← Point d'entrée CLI
├── usecases/run_experiment.py  ← Pipeline complet (use case)
├── domain/                     ← Entités, engine, scorer
├── adapters/                   ← LLM (LiteLLM), exports (JSON, figures)
└── ports/                      ← Interfaces abstraites

config/
└── models.yaml                 ← Registry des modèles

datasets/sfar_antibioprophylaxie/
├── benchmark.md                ← Questions (source de vérité)
├── benchmark.json              ← Questions compilées
├── md_to_json.py               ← Convertir MD → JSON
└── json_to_md.py               ← Convertir JSON → MD

research/
├── results/                    ← Résultats JSON par run
└── figures/                    ← Figures PNG générées
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
