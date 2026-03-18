# Plan d'implémentation : llm-benchmark

## Vue d'ensemble

Implémentation du cadre d'évaluation `medical-llm-benchmark` en Python 3.12, suivant l'architecture hexagonale (ports et adaptateurs), les principes DDD (Value Objects), et le TDD (tests avant code, coverage ≥ 80% sur la logique métier).

Le code existant (`scripts/run_benchmark.py`, `scripts/benchmark_md_to_json.py`, `research/benchmark.json`) sert de référence fonctionnelle ; la migration vers la nouvelle architecture est l'objectif principal.

## Tâches

- [-] 1. Mettre en place la structure du projet et les Value Objects du domaine
  - Créer l'arborescence `src/llm_benchmark/domain/`, `ports/`, `adapters/`, `config/`, `cli/` et `tests/unit/`, `tests/property/`, `tests/integration/`
  - Créer `src/llm_benchmark/domain/value_objects.py` avec les frozen dataclasses : `Cost`, `Latency`, `CarbonFootprint`, `Accuracy`, `ModelId`, `ApproachId`, `DatasetId`, `RunId`, `QuestionId`, `DatasetVersion`, `Source`, `MCQChoices`, `QuestionType`
  - Chaque Value Object valide ses invariants dans `__post_init__` (valeurs négatives, chaînes vides, clés QCM invalides, précision hors [0,1])
  - Mettre à jour `pyproject.toml` : ajouter `codecarbon`, `marimo`, `hypothesis`, `pyyaml` aux dépendances ; configurer `[tool.pytest.ini_options]` avec `testpaths = ["tests"]` et coverage sur `src/`
  - _Requirements : 1.1, 1.2, 2.1, 2.2, 2.3_

  - [ ] 1.1 Écrire les tests unitaires des Value Objects
    - Tester les invariants de chaque Value Object (valeurs limites, cas invalides)
    - Tester `Accuracy.as_percent`
    - Tester `MCQChoices` avec clés invalides et dict vide
    - _Requirements : 1.2, 1.3_

  - [ ] 1.2 Écrire les tests de propriété pour les Value Objects
    - **Propriété 1 : Immuabilité** — tout Value Object frozen lève `FrozenInstanceError` à toute tentative de mutation
    - **Valide : Requirements 2.1, 2.2, 2.3**
    - **Propriété 2 : Invariants Cost** — `Cost(amount, currency)` est valide ssi `amount >= 0` et `currency in {"USD","EUR"}`
    - **Valide : Requirements 5.3**
    - **Propriété 3 : Invariants Accuracy** — `Accuracy(v)` est valide ssi `0.0 <= v <= 1.0` ; `as_percent == v * 100`
    - **Valide : Requirements 4.6**

- [ ] 2. Définir les entités du domaine et les ports
  - Créer `src/llm_benchmark/domain/entities.py` avec les dataclasses : `Question`, `Dataset`, `LLMRequest`, `LLMResponse`, `ScoreResult`, `QuestionResult`, `RunSummary`, `RunResult`
  - Créer `src/llm_benchmark/ports/approach.py` : ABC `ApproachPort` avec `approach_id`, `build_prompt`, `prepare`
  - Créer `src/llm_benchmark/ports/llm.py` : ABC `LLMPort` avec `model_id`, `price_per_input_token`, `price_per_output_token`, `complete`
  - Créer `src/llm_benchmark/ports/export.py` : ABC `ExportPort` avec `export`
  - Créer `src/llm_benchmark/__init__.py` et `src/llm_benchmark/domain/__init__.py`, `ports/__init__.py`
  - _Requirements : 1.1, 1.5, 2.1, 2.2, 2.3, 3.3_

  - [ ] 2.1 Écrire les tests unitaires des entités
    - Tester la construction de `Question` (open et QCM), `Dataset`, `RunResult`
    - Vérifier que `Question` de type QCM requiert `choix` non nul
    - _Requirements : 1.2, 1.5_

- [ ] 3. Implémenter le chargeur de jeu de données et migrer le dataset SFAR
  - Créer `src/llm_benchmark/domain/dataset_loader.py` : fonction `load_dataset(path: Path) -> Dataset` qui lit le JSON, valide la structure (champs obligatoires : id, type, question, réponse, source), et lève `DatasetValidationError` avec la liste des erreurs si invalide
  - Créer `datasets/sfar_antibioprophylaxie/benchmark.json` en migrant `research/benchmark.json` vers le nouveau format (champ `"type": "mcq"` au lieu de `"qcm"`, champ `"choix"` renommé en `"choices"` si nécessaire — vérifier la cohérence avec les entités)
  - Créer `datasets/sfar_antibioprophylaxie/metadata.yaml` avec les métadonnées du jeu de données
  - _Requirements : 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.2_

  - [ ] 3.1 Écrire les tests unitaires du chargeur
    - Tester le chargement d'un dataset valide (open + QCM)
    - Tester le rejet d'un dataset avec champs manquants (liste d'erreurs retournée)
    - Tester le rejet d'un dataset avec type inconnu
    - _Requirements : 1.2, 1.3_

  - [ ] 3.2 Écrire les tests de propriété pour le chargeur
    - **Propriété 4 : Rejet exhaustif** — pour tout JSON dont au moins une question manque un champ obligatoire, `load_dataset` lève `DatasetValidationError` et la liste d'erreurs est non vide
    - **Valide : Requirements 1.3**

- [ ] 4. Implémenter les évaluateurs (scorers)
  - Créer `src/llm_benchmark/domain/scorer.py` avec :
    - `normalize(text: str) -> str` : minuscules, strip, espaces multiples, ponctuation finale
    - `OpenScorer` : vérifie la présence de chaque molécule attendue (split sur "+") dans la réponse normalisée ; cas "Non" → cherche "non" ou "pas d'"
    - `QCMScorer` : extrait la lettre A–D par regex `\b([A-D])\b` et compare à la lettre attendue
    - `SourcingScorer` : détecte une référence explicite dans la réponse ; vérifie la correspondance avec `Question.source`
    - `ScorerRegistry` : dict `{QuestionType: scorer}` avec méthode `score(question, actual) -> ScoreResult`
  - _Requirements : 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 6.1, 6.2_

  - [ ] 4.1 Écrire les tests unitaires des scorers
    - Tester `OpenScorer` : molécule unique, association "+", "Non", "Hors périmètre", casse mixte
    - Tester `QCMScorer` : lettre seule, lettre dans phrase, réponse invalide
    - Tester `SourcingScorer` : présence/absence de référence, correspondance correcte/incorrecte
    - Tester `ScorerRegistry` avec les deux types de questions
    - _Requirements : 4.1, 4.2, 4.3, 4.4, 6.1, 6.2_

  - [ ] 4.2 Écrire les tests de propriété pour les scorers
    - **Propriété 5 : Déterminisme** — pour tout couple `(expected, actual)`, `scorer.score` retourne toujours le même `ScoreResult`
    - **Valide : Requirements 4.1, 4.2**
    - **Propriété 6 : Symétrie de la normalisation** — `normalize(normalize(s)) == normalize(s)` pour toute chaîne `s`
    - **Valide : Requirements 4.1**
    - **Propriété 7 : Correction QCM** — `QCMScorer` retourne `correct=True` ssi la lettre extraite correspond exactement à la lettre attendue
    - **Valide : Requirements 4.2**

- [ ] 5. Checkpoint — Vérifier que tous les tests passent
  - S'assurer que `pytest tests/unit tests/property -v` passe sans erreur.
  - Vérifier que la couverture de `src/llm_benchmark/domain/` est ≥ 80%.
  - Demander à l'utilisateur si des ajustements sont nécessaires avant de continuer.

- [ ] 6. Implémenter le collecteur de métriques
  - Créer `src/llm_benchmark/domain/metrics.py` avec `MetricsCollector` :
    - Méthode `start_run() -> None` : démarre le tracker CodeCarbon (`EmissionsTracker`)
    - Méthode `stop_run() -> CarbonFootprint | None` : arrête le tracker et retourne l'empreinte
    - Méthode `compute_cost(llm: LLMPort, response: LLMResponse) -> Cost | None` : calcule le coût à partir des jetons et des tarifs du port LLM
    - Si CodeCarbon n'est pas disponible ou échoue, retourner `None` sans lever d'exception
  - _Requirements : 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ] 6.1 Écrire les tests unitaires du collecteur de métriques
    - Tester `compute_cost` avec des tarifs connus et des comptes de jetons variés
    - Tester le comportement quand `input_tokens` ou `output_tokens` est `None`
    - Tester que `stop_run` retourne `None` si CodeCarbon n'est pas initialisé
    - _Requirements : 5.3, 5.5_

- [ ] 7. Implémenter le moteur du banc d'essai (`BenchmarkEngine`)
  - Créer `src/llm_benchmark/domain/engine.py` avec `BenchmarkEngine` :
    - Méthode `run(dataset, approaches, llms, question_ids=None) -> list[RunResult]`
    - Pour chaque combinaison (approche × LLM) : appeler `approach.prepare()`, itérer sur les questions filtrées, appeler `approach.build_prompt`, `llm.complete`, `scorer.score`, `metrics_collector.compute_cost`
    - Enregistrer les erreurs LLM dans `QuestionResult.error` et poursuivre (requirements 3.4)
    - Afficher la progression question par question (requirements 3.7)
    - Calculer `RunSummary` : total, correct, accuracy, sourcing_rate, sourcing_correct_rate, total_cost, total_tokens, avg_latency, carbon_footprint, by_type
    - Générer `RunId` (UUID4) et horodatage UTC pour chaque `RunResult`
  - _Requirements : 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, 5.1, 5.2, 5.3, 5.4, 6.3, 6.4_

  - [ ] 7.1 Écrire les tests unitaires du moteur
    - Tester avec des doubles (stubs) pour `ApproachPort` et `LLMPort`
    - Vérifier que les erreurs LLM sont enregistrées sans interrompre l'exécution
    - Vérifier que le filtre `question_ids` fonctionne correctement
    - Vérifier que `RunResult` contient un `run_id` unique et un `timestamp`
    - _Requirements : 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 7.2 Écrire les tests de propriété pour le moteur
    - **Propriété 8 : Unicité des run_id** — deux appels successifs à `engine.run` produisent des `RunId` distincts
    - **Valide : Requirements 3.2**
    - **Propriété 9 : Cohérence du résumé** — `summary.correct <= summary.total` et `summary.accuracy == correct / total` pour tout `RunResult`
    - **Valide : Requirements 3.3, 4.6**

- [ ] 8. Implémenter les adaptateurs d'export
  - Créer `src/llm_benchmark/adapters/exports/json_export.py` : `JsonExportAdapter(ExportPort)` sérialise `RunResult` en JSON structuré (schéma défini dans le design), retourne le `Path` du fichier créé
  - Créer `src/llm_benchmark/adapters/exports/csv_export.py` : `CsvExportAdapter(ExportPort)` exporte un rapport comparatif de plusieurs `RunResult` en CSV (une ligne par combinaison approche × LLM)
  - Créer `src/llm_benchmark/adapters/exports/__init__.py`
  - _Requirements : 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 8.1 Écrire les tests unitaires des adaptateurs d'export
    - Tester que `JsonExportAdapter` produit un JSON valide avec le bon schéma (run_id, timestamp, summary, results)
    - Tester que `CsvExportAdapter` produit un CSV avec les colonnes attendues
    - Tester que les deux adaptateurs retournent un `Path` existant après export
    - _Requirements : 7.1, 7.2, 7.4_

  - [ ] 8.2 Écrire les tests de propriété pour l'export JSON
    - **Propriété 10 : Schéma stable** — pour tout `RunResult` valide, le JSON exporté contient exactement les clés de premier niveau définies dans le design (`run_id`, `timestamp`, `dataset_id`, `dataset_version`, `approach_id`, `model_id`, `framework_version`, `config`, `summary`, `results`)
    - **Valide : Requirements 7.4**

- [ ] 9. Implémenter le chargeur de configuration YAML
  - Créer `src/llm_benchmark/config/loader.py` : fonction `load_config(path: Path) -> BenchmarkConfig` qui lit un fichier YAML et valide les champs obligatoires (dataset, approaches, llms)
  - Définir `BenchmarkConfig` comme dataclass avec les champs : `dataset_path`, `approaches`, `llms`, `output_dir`, `question_ids`
  - Lever `ConfigValidationError` avec message explicite si un champ obligatoire est absent
  - _Requirements : 2.6, 8.1, 8.8_

  - [ ] 9.1 Écrire les tests unitaires du chargeur de configuration
    - Tester le chargement d'une config valide
    - Tester le rejet d'une config avec champs manquants
    - _Requirements : 2.6, 8.8_

- [ ] 10. Implémenter l'adaptateur LLM universel via LiteLLM
  - Ajouter `litellm` aux dépendances dans `pyproject.toml`
  - Créer `src/llm_benchmark/adapters/llms/litellm_adapter.py` : `LiteLLMAdapter(LLMPort)` — wrapper LiteLLM exposant `model_id`, `price_per_input_token`, `price_per_output_token`, et `complete` retournant `LLMResponse` avec `input_tokens`, `output_tokens`, `latency`
  - Créer `config/models.yaml` : déclaration des modèles disponibles avec leurs tarifs (claude-sonnet, gpt-4o, mistral-large, etc.)
  - Créer `src/llm_benchmark/adapters/llms/__init__.py` et un registre `LLM_REGISTRY` chargé depuis `config/models.yaml`
  - Supprimer les scripts `scripts/run_benchmark.py` (remplacé par la nouvelle architecture)
  - _Requirements : 2.2, 3.1, 5.1, 5.2, 5.3, 5.5_

  - [ ] 10.1 Écrire les tests unitaires de l'adaptateur LiteLLM (avec mocks)
    - Mocker `litellm.completion` pour tester `complete` sans appel réseau
    - Vérifier que `LLMResponse` contient `input_tokens`, `output_tokens`, `latency`
    - Vérifier que les erreurs API LiteLLM sont propagées correctement
    - _Requirements : 3.4, 5.5_

- [ ] 11. Implémenter l'adaptateur d'approche "contexte long" (baseline)
  - Créer `src/llm_benchmark/adapters/approaches/long_context.py` : `LongContextApproach(ApproachPort)` — construit un prompt système contenant le texte complet des recommandations SFAR, `approach_id = ApproachId("long-context")`, `prepare()` charge le fichier source
  - Créer `src/llm_benchmark/adapters/approaches/__init__.py` et un registre `APPROACH_REGISTRY: dict[str, type[ApproachPort]]`
  - _Requirements : 2.1, 2.4, 2.7, 3.1_

  - [ ] 11.1 Écrire les tests unitaires de l'approche contexte long
    - Tester que `build_prompt` retourne une chaîne non vide contenant la question
    - Tester que `approach_id` retourne `ApproachId("long-context")`
    - _Requirements : 2.1, 2.4_

- [ ] 12. Implémenter la CLI
  - Créer `src/llm_benchmark/cli/main.py` avec `argparse` et les sous-commandes :
    - `run` : `--dataset`, `--approach` (multiple), `--model` (multiple), `--questions`, `--output-dir`, `--config`
    - `list approaches` / `list models` / `list datasets` / `list metrics` / `list runs`
    - `compare` : `--runs` (liste de fichiers JSON), `--output`
  - Retourner code de sortie non nul et message d'erreur explicite si paramètre manquant ou invalide
  - Ajouter le point d'entrée `llm-benchmark` dans `pyproject.toml` (`[project.scripts]`)
  - _Requirements : 3.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [ ] 12.1 Écrire les tests unitaires de la CLI
    - Tester chaque sous-commande avec `argparse` en mode test (sans appel réseau)
    - Tester le code de sortie non nul pour paramètres manquants
    - _Requirements : 8.1, 8.8_

- [ ] 13. Checkpoint — Intégration et câblage complet
  - Vérifier que `uv run llm-benchmark list models` fonctionne
  - Vérifier que `uv run llm-benchmark list datasets` liste `sfar_antibioprophylaxie`
  - Vérifier que `pytest -v --cov=src/llm_benchmark` passe avec coverage ≥ 80% sur le domaine
  - Demander à l'utilisateur si des ajustements sont nécessaires avant de continuer.

- [ ] 14. Implémenter le notebook Marimo d'exploration des résultats
  - Créer `notebooks/explore_results.py` : notebook Marimo avec :
    - Sélecteur de fichiers de résultats JSON (depuis `research/results/` ou `outputs/`)
    - Tableau comparatif des runs (accuracy, coût, latence, empreinte carbone)
    - Graphique de comparaison par type de question (open vs QCM)
    - Détail par question avec réponse attendue / obtenue / correct
    - Export du rapport comparatif en CSV via `CsvExportAdapter`
  - Le notebook doit être exécutable de manière reproductible : `marimo run notebooks/explore_results.py`
  - _Requirements : 10.1, 10.2, 10.3, 10.4_

- [ ] 15. Checkpoint final — Vérifier que tous les tests passent
  - Lancer `pytest -v --cov=src/llm_benchmark --cov-report=term-missing` et vérifier coverage ≥ 80%.
  - Lancer `ruff check src/ tests/` et corriger les éventuels problèmes de style.
  - Demander à l'utilisateur si des ajustements sont nécessaires.

## Notes

- Les tâches marquées `*` sont optionnelles et peuvent être ignorées pour un MVP rapide.
- Chaque tâche référence les exigences spécifiques pour la traçabilité.
- Les checkpoints (tâches 5, 13, 15) permettent une validation incrémentale.
- Les tests de propriété utilisent `hypothesis` ; les tests unitaires utilisent `pytest`.
- Le code existant dans `scripts/run_benchmark.py` sert de référence pour la logique métier (scoring, normalisation, appels API) mais ne doit pas être modifié — il sera remplacé par la nouvelle architecture.
- Les docstrings suivent le format numpydoc.
