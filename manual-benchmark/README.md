# Benchmark manuel « prompt + pièce jointe »

Approche **sans code** pour interroger n'importe quelle interface de chat
(ChatGPT, Mistral **Le Chat**, **Claude**, **MedGPT**…) : on colle un prompt,
on joint le fichier des questions, on récupère les réponses dans un format
toujours identique, puis on compare.

L'objectif est la **reproductibilité** : n'importe qui peut relancer le test
depuis un navigateur, sans clé API ni environnement Python.

## Deux modes de test

| Mode | Prompt | Pièces jointes | Ce qu'on mesure |
|------|--------|----------------|-----------------|
| **A — auto-documentation** | `prompts/mode-A-autodoc.md` | `questions.json` (ou `.md`) | connaissances propres de l'outil (± web) |
| **B — RFE fournie (RAG)** | `prompts/mode-B-rag.md` | **PDF des RFE** + `questions.json` | capacité à lire/appliquer le document |

## Contenu du dossier

| Fichier | Rôle |
|---------|------|
| `PROMPT.md` | Index des prompts (renvoie vers `prompts/`) |
| `prompts/mode-A-autodoc.md`, `prompts/mode-B-rag.md` | Prompts à copier-coller |
| `prompts/CHANGELOG.md` | Historique **SemVer** du prompt |
| `questions.json` | Les 171 questions **sans réponses** (pièce jointe structurée) |
| `questions.md` | Les mêmes en **texte brut** (outils refusant le JSON, ex. MedGPT) |
| `generate_questions.py` | Régénère `questions.json` **et** `questions.md` |
| `score_results.py` | Score les résultats collectés (hors-ligne, comparatif) |
| `results/` | Où déposer les JSON renvoyés (runs archivés dans des sous-dossiers datés) |

## Mode d'emploi

### 1. (Optionnel) Régénérer les questions

`questions.json` / `questions.md` sont déjà à jour. Après une modification du
dataset :

```bash
uv run python manual-benchmark/generate_questions.py
```

Le script retire le champ `réponse` de `benchmark.json` : le modèle interrogé
ne voit **jamais** la vérité terrain.

### 2. Interroger un outil

1. Ouvrir l'interface de chat.
2. Choisir le mode et coller le prompt correspondant (`prompts/mode-A-autodoc.md`
   ou `prompts/mode-B-rag.md`, bloc entre les lignes `─────`).
3. Joindre `questions.json` (ou coller `questions.md`). En **mode B**, joindre
   **aussi** le PDF des RFE.
4. Envoyer.

Le modèle répond par un **bloc JSON** conforme à ce schéma (v2) :

```json
{
  "modele": "GPT-4o",
  "date": "2026-07-18",
  "prompt_version": "2.0.0",
  "mode": "A",
  "dataset_version": "1.2",
  "reponses": [
    { "id": "Q01", "reponse": "Céfazoline" },
    { "id": "Q02", "reponse": "Pas d'antibioprophylaxie" }
  ]
}
```

Les champs `prompt_version`, `mode` et `dataset_version` assurent la
**traçabilité** : on sait toujours quel prompt et quel jeu de questions ont
produit un résultat. (Les runs plus anciens en schéma v1 restent lisibles ; le
scorer affiche `?` pour ces champs.)

### 3. Enregistrer le résultat

Copier le bloc JSON dans `results/`, nommé d'après l'outil. Pour archiver un
run reproductible (open science), le ranger dans un sous-dossier daté :

```text
manual-benchmark/results/2026-07-18/gpt-4o.json
manual-benchmark/results/2026-07-18/le-chat.json
```

> Les JSON déposés **en vrac à la racine** de `results/` ne sont pas versionnés
> (voir `.gitignore`), sauf `exemple.json`. Les **sous-dossiers datés** sont, eux,
> versionnés.

### 4. Comparer

```bash
python manual-benchmark/score_results.py manual-benchmark/results/2026-07-18/*.json
```

Exemple de sortie :

```text
Modèle                     Mode  Prompt   Global     Open      QCM  Manquantes
------------------------------------------------------------------------------
Claude Opus 4.8               A   2.0.0    83.6%    82.6%    87.9%           0
Le Chat                       A   2.0.0    72.5%    71.7%    75.8%           0
```

Le détail des erreurs (attendu vs obtenu) et des questions éventuellement
manquantes est affiché sous le tableau.

## Notes sur la notation

- La notation est **identique** à celle du pipeline automatisé
  (`src/llm_benchmark/domain/scorer.py`) : les deux approches sont donc
  directement comparables.
- **Questions ouvertes** : la réponse est correcte si toutes les molécules
  attendues apparaissent (comparaison insensible à la casse / aux espaces), ou si
  la mention exacte `Pas d'antibioprophylaxie` / `Hors périmètre` figure.
- **QCM** : la première lettre `A`–`D` trouvée est comparée à la lettre attendue.
- Si un outil tronque sa réponse, le prompt l'autorise à répondre en **plusieurs
  blocs JSON** (plages d'`id`) à concaténer ; sinon, scindez `questions.json`.

## Pistes futures

- **Scoring strict vs tolérant.** La notation actuelle est **stricte** : seule la
  molécule de **première intention** est acceptée. Or la RFE liste parfois des
  **alternatives** valides. Sur le run 2026-07-18, cela pénalise Q42
  (Amox/Clav = alternative listée à la céfazoline) et Q45 / Q131 (Céfazoline =
  moitié du combo alternatif). Une option `--tolerant` du scorer pourrait
  accepter les alternatives RFE — à condition de les encoder dans
  `benchmark.json`. Voir `results/2026-07-18/VERIFICATION-corrige.md`.
- **Versionnage du dataset.** Formaliser le SemVer des questions/réponses
  (`benchmark.json`) en miroir de celui du prompt, et recopier `dataset_version`
  dans chaque résultat (déjà prévu dans le schéma v2).
