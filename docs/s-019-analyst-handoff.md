# S-019 Analyst Handoff

Date: 2026-03-17
Story: `docs/s-019.md`
Phase: Pre-implementation cadrage

## Objectif

Finaliser un framework d'evaluation scientifique pour comparer 5 approches IA sur 25 questions d'antibioprophylaxie, avec mesure de precision, latence, couts, tokens, ecologie, et sourcage, puis produire une recommandation d'integration v2.

## Scope

- Completer `scripts/run_benchmark.py` pour execution multi-modeles et scoring automatise.
- Produire des resultats structures dans `research/results/`.
- Ajouter l'analyse comparative via `scripts/eval_results.py`.
- Generer `docs/findings-report.md`.

## Hors scope

- Construction complete des pipelines RAG/MCP/fine-tune de production si non necessaire au benchmark minimal reproductible.
- Evolution fonctionnelle de l'application principale SFAR.
- Refonte architecture lourde non requise par S-019.

## Criteres d'acceptation (etat)

- AC1 Dataset standardise: DONE (`research/benchmark.json`).
- AC2 Parser MD -> JSON: DONE (`scripts/benchmark_md_to_json.py`).
- AC3 Orchestrateur benchmark: IN PROGRESS (`scripts/run_benchmark.py`).
- AC4 Analyseur + rapport: TODO (`scripts/eval_results.py`, `docs/findings-report.md`).
- AC5 Documentation: TODO (README/docstrings/completion story).

## Criteres de verification operationnels

- `uv run python scripts/run_benchmark.py --list-models` fonctionne.
- Execution mono-modele cree un JSON valide dans `research/results/`.
- Execution multi-modeles cree un JSON par modele avec schema coherent.
- Les metriques minimales sont presentes: precision, latency, tokens, cout.
- `scripts/eval_results.py` agrege les resultats et produit un comparatif exploitable.

## Risques et mitigations

1. Risque: scoring trop naive (exact match strict) sous-estime la qualite reelle.
Mitigation: ajouter fuzzy match controle + regles QCM explicites + tests unitaires de scoring.

2. Risque: variabilite inter-runs LLM (temperature, indisponibilite API) rend comparaison fragile.
Mitigation: config deterministe (temperature basse), retries, journaux d'erreurs, metadonnees d'execution.

3. Risque: metriques cout/ecologie incompletes selon providers.
Mitigation: normaliser schema resultats avec champs optionnels et fallback explicites.

4. Risque: melange benchmark logique et experimentation RAG/MCP non stabilisee.
Mitigation: separer noyau benchmark (stable) et connecteurs systemes (adapters) testables.

5. Risque: absence de rapport final retarde la decision v2.
Mitigation: livrer un template de findings minimal puis enrichir.

## Dependances techniques

- Variables d'environnement API: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MISTRAL_API_KEY`.
- Outils: `uv`, `pytest`, `ruff`.
- Entrees: `research/benchmark.json`.
- Sorties: `research/results/*.json`, `docs/findings-report.md`.

## Plan propose (3-7 taches)

1. Stabiliser schema de sortie benchmark (resultat question + metadonnees run + metriques globales).
2. Finaliser scoring ouvert/QCM avec tests unitaires dedies.
3. Completer connecteurs modeles cibles et gestion d'erreurs/retries/timeouts.
4. Verrouiller commande CLI run benchmark (mono/multi modeles, list-models, paths output).
5. Implementer `scripts/eval_results.py` pour agregation et export comparatif.
6. Generer un premier `docs/findings-report.md` base sur resultats reels.
7. Clore AC5 avec docstrings et mise a jour README si ecarts.

## Questions ouvertes

- Definition precise de l'indicateur ecologie (source de conversion tokens -> g CO2e)?
- Regle canonique de fuzzy matching (seuil, normalisation accents, synonymes medicaux)?
- Liste finale des modeles obligatoires si contraintes budget/API apparaissent?

## Next step recommande

Passer a `bmad-dev-story` sur la base de ce handoff, en priorite AC3 puis AC4, avec verification continue via `uv run pytest` et `uv run ruff check .`.
