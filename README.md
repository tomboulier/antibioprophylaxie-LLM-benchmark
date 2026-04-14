# Antibioprophylaxie LLM Benchmark

Benchmark scientifique pour évaluer différentes approches d'IA appliquées aux [recommandations formalisées d'experts de la SFAR à propos de l'antibioprophylaxie en chirurgie et médecine interventionnelle](https://sfar.org/antibioprophylaxie-en-chirurgie-et-medecine-interventionnelle/).

## Objectif

### Initial

Evaluer différents modèles sur des questions standardisées sur ces recommandations.

### A terme

Comparer **5 systèmes** pour déterminer lequel est "meilleur" pour répondre aux questions d'antibioprophylaxie:

| Système | Description |
|---------|-------------|
| **RAG Niveau 1** | Retrieval sur PDF |
| **RAG Niveau 2** | Retrieval sur Excel structuré |
| **Long Context** | Tout le texte dans le contexte du modèle |
| **MCP Server** | Model Context Protocol avec tools |

## Données

- **Dataset de test**: jeu de questions avec réponses attendues (`datasets/sfar_antibioprophylaxie/benchmark.md`)
- **Source**: RFE SFAR 2024 ([V2.0 du 22/05/2024](https://sfar.org/download/antibioprophylaxie-en-chirurgie-et-medecine-interventionnelle/?wpdmdl=68362&refresh=69deb2e63ecc01776202470))

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
└── md_to_json.py               ← Convertir MD → JSON (numérotation auto)

research/
├── results/                    ← Résultats JSON par run
└── figures/                    ← Figures PNG générées
```

## Métriques

Pour le moment, seule la **précision** (% de réponses correctes) est testée.

Voici les autres métriques qui pourront être envisagées :
- **Consistance**: Taux d'accord sur N runs identiques (même question, même modèle) ; mesure la reproductibilité des réponses.
- **Sourçage**: Réponses incluent citation/source?
- **Latence**: Temps moyen par question (en secondes).
- **Coûts**: Tokens ou calories consommés.
- **Écologie**: Émissions CO2 estimées.

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
