# Benchmark manuel « prompt + pièce jointe »

Approche **sans code** pour interroger n'importe quelle interface de chat
(ChatGPT, Mistral **Le Chat**, **Claude**, **MedGPT**…) : on colle un prompt,
on joint le fichier des questions, on récupère les réponses dans un format
toujours identique, puis on compare.

L'objectif est la **reproductibilité** : n'importe qui peut relancer le test
depuis un navigateur, sans clé API ni environnement Python.

## Contenu du dossier

| Fichier | Rôle |
|---------|------|
| `PROMPT.md` | Le prompt à copier-coller dans le chat |
| `questions.json` | Les 171 questions **sans les réponses** (pièce jointe) |
| `generate_questions.py` | Régénère `questions.json` depuis `benchmark.json` |
| `score_results.py` | Score les résultats collectés (hors-ligne, comparatif) |
| `results/` | Où déposer les JSON renvoyés par chaque outil |

## Mode d'emploi

### 1. (Optionnel) Régénérer les questions

`questions.json` est déjà à jour. Après une modification du dataset :

```bash
uv run python manual-benchmark/generate_questions.py
```

Le script retire le champ `réponse` de `benchmark.json` : le modèle interrogé
ne voit **jamais** la vérité terrain.

### 2. Interroger un outil

1. Ouvrir l'interface de chat (ChatGPT, Le Chat, Claude, MedGPT…).
2. Coller le prompt de `PROMPT.md` (le bloc entre les lignes `─────`).
3. **Joindre `questions.json`** au même message.
4. Envoyer.

Le modèle répond par **un seul bloc JSON** conforme à ce schéma :

```json
{
  "modele": "GPT-4o",
  "date": "2026-07-18",
  "reponses": [
    { "id": "Q01", "reponse": "Céfazoline" },
    { "id": "Q02", "reponse": "Pas d'antibioprophylaxie" }
  ]
}
```

### 3. Enregistrer le résultat

Copier le bloc JSON renvoyé dans un fichier de `results/`, nommé d'après
l'outil, par exemple :

```
manual-benchmark/results/gpt-4o.json
manual-benchmark/results/le-chat.json
manual-benchmark/results/claude.json
manual-benchmark/results/medgpt.json
```

> `results/` n'est pas versionné par défaut (voir `.gitignore`), sauf le
> fichier d'exemple. À vous de décider si vous committez vos runs.

### 4. Comparer

```bash
python manual-benchmark/score_results.py manual-benchmark/results/*.json
```

Exemple de sortie :

```
Modèle                         Global     Open      QCM  Manquantes
-------------------------------------------------------------------
Claude                          92.4%    91.3%    97.0%           0
GPT-4o                          88.9%    87.7%    93.9%           0
```

Le détail des erreurs (attendu vs obtenu) et des questions éventuellement
manquantes est affiché sous le tableau.

## Notes

- La notation est **identique** à celle du pipeline automatisé
  (`src/llm_benchmark/domain/scorer.py`) : les deux approches sont donc
  directement comparables.
- **Questions ouvertes** : la réponse est correcte si toutes les molécules
  attendues apparaissent (comparaison insensible à la casse / accents d'espaces),
  ou si la mention exacte `Pas d'antibioprophylaxie` / `Hors périmètre` figure.
- **QCM** : la première lettre `A`–`D` trouvée est comparée à la lettre attendue.
- Si un outil tronque sa réponse (limite de contexte), relancez en demandant la
  suite, ou scindez `questions.json` en deux lots.
