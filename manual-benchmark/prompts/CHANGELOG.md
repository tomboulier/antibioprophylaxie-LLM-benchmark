# Changelog du prompt

Versionnage sémantique `MAJOR.MINOR.PATCH` :

- **MAJOR** — changement du **schéma de sortie** (casse la comparabilité des
  résultats entre versions).
- **MINOR** — reformulation des consignes pouvant **décaler les réponses**, à
  schéma de sortie inchangé.
- **PATCH** — coquille, clarification sans impact attendu sur les réponses.

Chaque résultat collecté doit référencer la `prompt_version` (et le `mode`) qui
l'a produit, pour rester traçable.

## 2.0.0 — 2026-07-18

Deux **modes** distincts (`mode-A-autodoc.md`, `mode-B-rag.md`) :
- **Mode A** — auto-documentation : l'outil répond de mémoire et/ou via le web,
  la RFE n'est pas fournie.
- **Mode B** — RAG fourni : le PDF des RFE est joint, réponse fondée dessus.

Changements par rapport à 1.0.0 :
- **Schéma de sortie enrichi** (⇒ bump MAJOR) : ajout de `prompt_version`,
  `mode`, `dataset_version` recopiés par l'outil. Les runs produits en 1.0.0
  restent en schéma v1 (sans ces champs) ; le scorer gère les deux.
- **Anti-refus** : suppression de la formulation *« exclusivement sur les RFE »*
  qui a fait refuser ChatGPT (il refusait de « prétendre » se fonder sur un
  document non joint). Remplacée par *« au mieux de ta connaissance des RFE »*
  (mode A) et une consigne explicite « le fichier ne contient que les
  questions, c'est voulu ».
- **Découpage autorisé** : l'outil peut répondre en plusieurs blocs JSON
  successifs (plages d'`id`) pour contourner la limite de longueur (autre motif
  de blocage de ChatGPT).
- **Première intention** explicitée pour les questions ouvertes.
- **Variante texte brut** `questions.md` mentionnée pour les outils refusant le
  JSON / les pièces jointes (ex. MedGPT).

## 1.0.0 — 2026-07-18 (initial)

Prompt unique (équivalent mode A), schéma de sortie `{ modele, date, reponses }`.
Fichier historique : `manual-benchmark/PROMPT.md` (voir l'historique git).
Utilisé pour le run `results/2026-07-18/`.

Limites constatées sur ce run :
- ChatGPT **refuse** (consigne « exclusivement » jugée contradictoire + longueur).
- MedGPT **bloque** sur le JSON et n'accepte pas de pièce jointe.
