# Prompts — index

Les prompts à copier-coller vivent dans [`prompts/`](./prompts), versionnés
sémantiquement (voir [`prompts/CHANGELOG.md`](./prompts/CHANGELOG.md)).

Deux **modes** de test, selon ce qu'on fournit à l'outil :

| Mode | Fichier | Ce qu'on joint | Ce qu'on mesure |
|------|---------|----------------|-----------------|
| **A — auto-documentation** | [`prompts/mode-A-autodoc.md`](./prompts/mode-A-autodoc.md) | `questions.json` (ou `questions.md`) | connaissances propres de l'outil (± web) sur les RFE |
| **B — RFE fournie (RAG)** | [`prompts/mode-B-rag.md`](./prompts/mode-B-rag.md) | le **PDF des RFE** + `questions.json` | capacité à lire et appliquer le document fourni |

Dans les deux cas, l'outil répond par un **bloc JSON** au schéma standard
(champs `prompt_version`, `mode`, `dataset_version` + `reponses`). On enregistre
le résultat dans [`results/`](./results) puis on score avec
[`score_results.py`](./score_results.py). Voir [`README.md`](./README.md) pour le
mode d'emploi complet.

> Pièces jointes : `questions.json` (structuré, défaut) ou `questions.md` (texte
> brut, pour les outils qui refusent le JSON / les pièces jointes, ex. MedGPT).
> Les deux sont générés par `generate_questions.py`.

Le prompt v1.0.0 (unique, utilisé pour le run `results/2026-07-18/`) est conservé
dans l'historique git.
