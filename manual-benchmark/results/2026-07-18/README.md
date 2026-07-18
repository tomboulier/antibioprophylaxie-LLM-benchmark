# Run manuel — 2026-07-18

Premier test du protocole « prompt + `questions.json` collés dans une interface
de chat grand public ». Mode testé : **auto-documentation** (l'outil se débrouille
seul — connaissances internes et/ou recherche web ; la RFE n'est PAS fournie en
pièce jointe).

Notation via `manual-benchmark/score_results.py` (mêmes règles que le pipeline).

## Résultats

| Outil | Statut | Global | Ouvertes | QCM | n |
|-------|--------|:---:|:---:|:---:|:---:|
| **Claude Opus 4.8** | complet | **83,6 %** | 82,6 % | 87,9 % | 171 |
| **Le Chat (Mistral)** | complet | **72,5 %** | 71,7 % | 75,8 % | 171 |
| **MedGPT** | partiel / reformaté | *(6/8)* | *(3/5)* | *(3/3)* | 8 |
| **ChatGPT** | refus | — | — | — | 0 |

> ⚠️ Le score MedGPT porte sur **8 questions** seulement (163 manquantes) : il
> n'est **pas comparable** aux runs complets et ne doit pas figurer comme tel
> dans un comparatif agrégé.

## Fichiers

- `claude-opus-4.8.json` — run complet, format respecté à la lettre.
- `le-chat.json` — run complet (l'export était nommé « Le Chat »).
- `medgpt-partiel-brut.json` — sortie **brute** de MedGPT (texte libre verbeux).
- `medgpt-partiel.json` — sortie **reformatée** manuellement au format canonique
  (table de correspondance ci-dessous).
- ChatGPT : aucun JSON produit (refus, voir §MedGPT/ChatGPT).

## MedGPT — reformatage manuel

MedGPT **n'accepte ni le JSON en entrée ni de pièce jointe**, et bloque quand
l'invite contient du structuré. Seules 8 réponses (Q01–Q05, Q169–Q171) ont pu
être obtenues, en texte libre, avant d'atteindre le quota journalier. Extraction
fidèle (on transcrit ce que MedGPT a dit, sans corriger vers la bonne réponse) :

| id | Sortie brute (abrégée) | Format canonique |
|----|----|----|
| Q01 | « Céfazoline 2 g IV… » | `Céfazoline` |
| Q02 | « Pas d'antibioprophylaxie systématique… » | `Pas d'antibioprophylaxie` |
| Q03 | « Vancomycine IV… ± agent gram‑négatifs… » | `Vancomycine` |
| Q04 | « Vancomycine IV… alternative à la céfazoline… » | `Vancomycine` |
| Q05 | « …par exemple **céfazoline ou céfuroxime**… » | ⚠️ `Céfazoline` *(interprété)* |
| Q169 | « B » | `B` |
| Q170 | « C » | `C` |
| Q171 | « C » | `C` |

Q05 est litigieux : MedGPT a répondu de façon *curative* et n'a pas tranché une
molécule unique. Item faux quoi qu'il arrive (attendu `Amoxicilline/Clavulanate`).

## ChatGPT — refus (résultat en soi)

ChatGPT n'a produit aucune réponse. Objection en deux temps :

1. **Consigne jugée contradictoire** — le prompt demande de se fonder
   *« exclusivement sur les RFE SFAR 2024 »*, mais la pièce jointe *« ne contient
   que les questions, pas les réponses officielles »*. ChatGPT refuse de
   « prétendre » une conformité à un document qu'il n'a pas.
2. **Longueur** — après avoir accepté d'aller chercher les RFE en ligne, il
   estime que 171 réponses dépassent une seule réponse et propose un découpage en
   5 lots… sans finalement produire le JSON.

→ Ce refus est un **défaut de formulation du prompt v1**, pas un échec du modèle.
Il motive un **prompt v2** (voir plus bas).

## Désaccords partagés — VÉRIFIÉS ✅

Items où **Claude ET Le Chat donnent la MÊME réponse, contraire au corrigé**.
Recroisés un par un avec le PDF de la RFE → **corrigé correct 14/14** ; ce sont
les modèles qui ratent les exceptions de tableau. Détail et preuves dans
[`VERIFICATION-corrige.md`](./VERIFICATION-corrige.md).

| id | Réponse commune des 2 modèles | Corrigé actuel |
|----|----|----|
| Q04 | Clindamycine | Vancomycine |
| Q27 | Vancomycine | Clindamycine |
| Q42 | Amoxicilline/Clavulanate | Céfazoline |
| Q45 | Céfazoline | Amoxicilline/Clavulanate |
| Q63 | Céfazoline | Amoxicilline/Clavulanate |
| Q69 | Pas d'antibioprophylaxie | Céfazoline |
| Q71 | Céfazoline | Céfoxitine |
| Q91 | Pas d'antibioprophylaxie | Métronidazole |
| Q114 | Pas d'antibioprophylaxie | Céfazoline |
| Q131 | Céfazoline | Amoxicilline/Clavulanate |
| Q136 | Céfazoline | Pas d'antibioprophylaxie |
| Q142 | C | B |
| Q143 | B | C |
| Q154 | A | C |

## Biais notables

- **Le Chat** sur-prescrit `Céfazoline + Métronidazole` en chirurgie digestive
  (≈ Q85–Q116) là où le corrigé attend `Céfoxitine` ou `Pas d'antibioprophylaxie`
  → biais systématique (couverture anaérobie ajoutée par défaut).
