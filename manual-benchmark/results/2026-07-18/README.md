# Run manuel — 2026-07-18

Test du protocole « prompt + questions collés dans une interface de chat grand
public », dans les **deux modes** :
- **Mode A — auto-documentation** (prompt v1.0.0 puis v2.0.0) : l'outil se
  débrouille seul (connaissances / web), la RFE n'est PAS fournie ;
- **Mode B — RAG** (prompt v2.0.0) : le PDF des RFE est joint en pièce jointe.

Notation via `manual-benchmark/score_results.py` (mêmes règles que le pipeline).

## Mode A — auto-documentation (171 questions)

| Outil | Statut | Global | Ouvertes | QCM |
|-------|--------|:---:|:---:|:---:|
| **Claude Opus 4.8** | complet | **83,6 %** | 82,6 % | 87,9 % |
| **Le Chat (Mistral)** | complet | **72,5 %** | 71,7 % | 75,8 % |
| **GPT-5.5-mini (ChatGPT)** | complet | **72,5 %** | 69,6 % | 84,8 % |
| **MedGPT** | partiel / reformaté | *(6/8)* | *(3/5)* | *(3/3)* |

> ⚠️ Le score MedGPT porte sur **8 questions** seulement : non comparable.
> **ChatGPT a été débloqué par le prompt v2** (il refusait en v1) ; il s'identifie
> comme *GPT-5.5-mini*, un modèle de tier « mini » — d'où un score proche du Chat.

## Mode B — RFE jointe (RAG, 171 questions)

| Outil | Statut | Global | Ouvertes | QCM |
|-------|--------|:---:|:---:|:---:|
| **Claude Opus 4.8** | complet | **98,2 %** | 98,6 % | 97,0 % |
| **Mistral Large 2** | complet | **83,0 %** | 83,3 % | 81,8 % |

### Fournir la RFE fait bondir la précision

| Modèle | Mode A | Mode B | Δ |
|--------|:---:|:---:|:---:|
| Claude Opus 4.8 | 83,6 % | **98,2 %** | **+14,6 pts** |
| Mistral | 72,5 % | **83,0 %** | **+10,5 pts** |

Le RAG corrige quasiment tous les pièges du mode A (Q04, Q27, Q42, Q45, Q69, Q71,
Q91, Q114, Q131, Q136, Q142, Q154 deviennent justes). **Claude mode B ne laisse
que 3 erreurs / 171** :
- **Q15** : Céfazoline au lieu d'Amox/Clav ;
- **Q90** : a repéré la note BLSE (« antibioprophylaxie active sur la souche
  identifiée ») mais pas la molécule précise (Ertapénème) ;
- **Q143** : toujours le piège « plaie de la **main** » (B au lieu de C) — **ce
  piège survit au RAG**.

### Mistral mode B : le RAG « décroche » au fil des lots

Mistral a répondu en **plusieurs messages** (arrêt à Q50, relances successives).
Sa précision s'effondre après le premier lot — signe qu'il **perd le contexte du
PDF** entre les messages :

| Segment | Q01–Q50 | Q51–Q100 | Q101–Q171 |
|---------|:---:|:---:|:---:|
| Mistral mode B | 96,0 % | 72,0 % | 81,7 % |
| Claude mode B (réf.) | 98,0 % | — | 98,6 % |

Claude, lui, reste à ~98 % partout → la chute est **spécifique à Mistral**, pas
une question de difficulté. **Leçon protocole** : pour le mode B, privilégier une
réponse en **un seul message** ; si découpage nécessaire, **re-joindre le PDF** à
chaque relance.

## Fichiers

**Mode A :**
- `claude-opus-4.8.json` — run complet, format respecté à la lettre.
- `le-chat.json` — run complet (export nommé « Le Chat »).
- `chatgpt-gpt5.5-mini-modeA.json` — run complet (prompt v2 ; s'identifie GPT-5.5-mini).
- `medgpt-partiel.json` / `medgpt-partiel-brut.json` — 8 réponses reformatées + brut.

**Mode B :**
- `claude-opus-4.8-modeB.json` — run complet 171.
- `mistral-modeB.json` — run complet 171 (reconstitué à partir de lots successifs).

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

## ChatGPT — refus en v1, débloqué en v2

En **prompt v1**, ChatGPT n'a produit aucune réponse. Objection en deux temps :

1. **Consigne jugée contradictoire** — le prompt demande de se fonder
   *« exclusivement sur les RFE SFAR 2024 »*, mais la pièce jointe *« ne contient
   que les questions, pas les réponses officielles »*. ChatGPT refuse de
   « prétendre » une conformité à un document qu'il n'a pas.
2. **Longueur** — après avoir accepté d'aller chercher les RFE en ligne, il
   estime que 171 réponses dépassent une seule réponse et propose un découpage en
   5 lots… sans finalement produire le JSON.

→ Ce refus était un **défaut de formulation du prompt v1**, pas un échec du
modèle. Le **prompt v2** (anti-refus + découpage autorisé) l'a **débloqué** :
ChatGPT a répondu aux 171 questions en mode A (voir tableau Mode A).

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
