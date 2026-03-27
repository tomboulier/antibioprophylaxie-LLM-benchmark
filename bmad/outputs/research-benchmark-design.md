# Bonnes pratiques pour la conception de benchmarks medicaux LLM

> Recherche documentaire -- 2026-03-27
> Contexte : benchmark antibioprophylaxie SFAR 2024, dataset actuel de 23 questions

---

## 1. Combien de questions pour un benchmark credible ?

Les benchmarks publies couvrent un large spectre :

| Benchmark | Taille | Domaine |
|-----------|--------|---------|
| AMEGA | 135 questions, 1 337 elements de scoring | Adherence aux guidelines, 13 specialites |
| HealthBench (OpenAI) | 5 000 conversations, 48 562 criteres de rubrique | Sante generale |
| MedQA (USMLE) | 12 723 questions (EN) | Examen medical general |
| PubMedQA | 1 000 annotees expert + 211k generees | Questions de recherche biomedicale |
| MedBench | 300 901 questions | 43 specialites cliniques (chinois) |
| MedThink-Bench | 500 questions haute complexite | 10 domaines medicaux |
| CSEDB | 2 069 Q&A ouvertes | 26 departements cliniques, securite |
| Swedish SMLB | ~4 datasets combines | Medecine suedoise |

**Pour un benchmark mono-guideline (comme le notre) :**

- Un minimum de **50 a 100 questions** est necessaire pour obtenir des intervalles de confiance exploitables lors de la comparaison de systemes.
- AMEGA, le benchmark le plus proche du notre (adherence aux guidelines), utilise 135 questions avec 1 337 elements de scoring ponderes -- c'est une reference directe.
- En dessous de 50 questions, les differences de performance entre modeles ne seront pas statistiquement significatives (puissance trop faible pour detecter des effets < 10 points de pourcentage).
- **Recommandation : viser 60-80 questions**, chacune avec plusieurs criteres de scoring (comme AMEGA), ce qui donne un dataset effectif bien plus large.

Sources : [AMEGA -- npj Digital Medicine](https://www.nature.com/articles/s41746-024-01356-6), [HealthBench -- OpenAI](https://openai.com/index/healthbench/), [MedQA](https://www.vals.ai/benchmarks/medqa)

---

## 2. Types de questions recommandes

La litterature identifie un compromis clair :

### QCM (Multiple Choice Questions)
- **Avantages** : scoring automatique, reproductible, pas de juge humain.
- **Inconvenients** : risque de data leakage (memorisation), ne reflete pas la pratique clinique reelle, sensible au format des choix.
- **Usage** : evaluation initiale rapide, screening.

### Questions ouvertes (free-text)
- **Avantages** : meilleure validite ecologique, permet d'evaluer le raisonnement.
- **Inconvenients** : necessite un juge (humain ou LLM-as-judge), plus complexe a scorer.
- **Usage** : evaluation approfondie, scoring par rubrique.

### Vignettes cliniques
- **AMEGA et HealthBench** utilisent des scenarios cliniques realistes (multi-tour, multi-etapes).
- **CPGPrompt** convertit les guidelines en arbres de decision et genere des vignettes de patients synthetiques.
- **Usage** : ideal pour tester l'application de guidelines a des cas concrets.

### Recommandation pour notre benchmark

Adopter un **mix** :
- **~40% questions ouvertes simples** (molecule, oui/non) -- scoring exact match, facile a automatiser.
- **~30% QCM** -- couverture de connaissances factuelles (doses, intervalles, classifications).
- **~30% vignettes cliniques** -- scenarios avec comorbidites, allergies, cas limites. Scoring par rubrique multi-criteres.

Sources : [Swedish SMLB](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full), [CSEDB -- Nature](https://www.nature.com/articles/s41746-025-02277-8), [Construct Validity -- arXiv](https://arxiv.org/html/2503.10694v1)

---

## 3. Structurer les questions pour qu'elles soient non ambigues et scorables

### Principes issus de la litterature

1. **Une question = un concept teste**. Eviter les questions composites sauf si c'est l'objet du test.
2. **Reponse de reference explicite et unique**. Pour les questions ouvertes, definir les synonymes acceptes (ex : "Amoxicilline-Clavulanate" = "Augmentin" = "Amoxicilline/acide clavulanique").
3. **Rubrique de scoring multi-criteres** (modele HealthBench/AMEGA) :
   - Chaque question a N criteres binaires ou ponderes.
   - Exemple : "Bonne molecule" (2 pts) + "Bonne dose" (1 pt) + "Bonne duree" (1 pt) + "Mentionne l'allergie" (1 pt).
4. **Eviter les negations dans les QCM** ("laquelle ne necessite PAS...") -- source connue de biais.
5. **Fournir le contexte minimal necessaire** : poids du patient, allergie, type de chirurgie.

### Scoring automatise

- **Exact match** pour les reponses courtes (molecule, oui/non).
- **LLM-as-judge** pour les reponses longues, calibre sur des annotations humaines. HealthBench rapporte un macro F1 = 0.71 pour GPT-4.1 vs. medecins.
- **Scoring pondere** par importance clinique (AMEGA : 1 337 elements ponderes pour 135 questions, soit ~10 criteres/question).

Sources : [HealthBench paper](https://arxiv.org/abs/2505.08775), [AMEGA GitHub](https://github.com/DATEXIS/AMEGA-benchmark/)

---

## 4. Niveaux de difficulte et couverture

### Niveaux de difficulte

Trois niveaux sont standard :

| Niveau | Description | Exemple dans notre contexte |
|--------|-------------|-----------------------------|
| **Facile** | Rappel factuel direct | "Molecule pour PTH ?" -> Cefazoline |
| **Moyen** | Application avec contexte | "Patient allergique, PTH voie anterieure ?" |
| **Difficile** | Raisonnement multi-etapes, cas limites | "Gustilo 3 + allergie penicilline + insuffisance renale : molecule, dose, duree ?" |

HealthBench publie un sous-ensemble "Hard" ou le meilleur modele ne score que 32%.

### Couverture thematique

- **MedBench** utilise une taxonomie a 5 dimensions (comprehension, generation, Q&A, raisonnement, securite/ethique).
- **AMEGA** couvre 13 specialites avec 20 scenarios.
- **Pour notre benchmark** : couvrir systematiquement chaque section du RFE SFAR (ortho programmee, traumato, etc.) et chaque type de decision (molecule, dose, reinjection, absence d'indication, allergie, cas special).

**Recommandation** : creer une matrice couverture (section RFE x type de decision x difficulte) et s'assurer qu'il n'y a pas de trous.

Sources : [MedThink-Bench](https://www.nature.com/articles/s41746-025-02208-7), [HealthBench Hard](https://huggingface.co/datasets/openai/healthbench)

---

## 5. Validation des reponses de reference

### Methodes utilisees par les benchmarks publies

| Methode | Benchmark | Detail |
|---------|-----------|--------|
| Consensus de medecins | HealthBench | 262 medecins, 60 pays |
| Expert panel + CVI | CSEDB | Medecins specialistes, Content Validity Index |
| Examen officiel | MedQA, SMLB | Questions d'examen deja validees |
| Guidelines officielles | AMEGA | Extraction directe des recommandations |
| Gold-standard rater | Divers | Un expert de reference, kappa inter-evaluateurs |

### Recommandation pour notre benchmark

1. **Source primaire** : les RFE SFAR 2024 elles-memes (chaque reponse doit etre tracable a une section precise).
2. **Validation par un medecin anesthesiste** : minimum 1 expert relit toutes les questions + reponses attendues (idealement 2 pour calcul de kappa).
3. **Mesure inter-evaluateurs** : si 2+ experts, calculer le Cohen's kappa (objectif >= 0.8 = accord quasi-parfait).
4. **Pilot test** : faire passer le benchmark a 2-3 medecins humains pour verifier que les questions sont claires et que les reponses attendues sont correctes.

Sources : [HealthBench methodology](https://cdn.openai.com/pdf/bd7a39d5-9e9f-47b3-903c-8b847ca650c7/healthbench_paper.pdf), [Inter-rater reliability guide](https://www.americandatanetwork.com/clinical-data-abstraction/the-ultimate-guide-to-inter-rater-reliability-in-clinical-data-abstraction-unlock-unmatched-accuracy/)

---

## 6. Metadonnees recommandees par question

En synthetisant les schemas des benchmarks majeurs, voici les champs recommandes :

```json
{
  "id": "Q01",
  "title": "Protocole standard PTH",
  "type": "open | qcm | vignette",
  "difficulty": "easy | medium | hard",
  "category": "ortho-programmee | traumatologie | cas-special",
  "subcategory": "prothese | rachis | fracture-ouverte | allergie",
  "source_section": "ortho-prog-mi-prothese-hanche-genou",
  "source_page": "p.12",
  "question": "...",
  "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "expected_answer": "Cefazoline",
  "accepted_synonyms": ["cefazoline", "Kefzol", "cephazolin"],
  "scoring_rubric": [
    {"criterion": "bonne_molecule", "weight": 2, "expected": "Cefazoline"},
    {"criterion": "bonne_dose", "weight": 1, "expected": "2g IVL"},
    {"criterion": "bonne_duree", "weight": 1, "expected": "dose unique ou 24h max"}
  ],
  "clinical_impact": "high | medium | low",
  "validated_by": "Dr X, Dr Y",
  "validation_date": "2026-04-15",
  "tags": ["betalactamine", "premiere-intention", "membre-inferieur"]
}
```

**Champs critiques (a ajouter en priorite)** :
- `difficulty` -- absent du dataset actuel.
- `scoring_rubric` -- transformer le simple exact-match en grille multi-criteres.
- `accepted_synonyms` -- reduire les faux negatifs de scoring.
- `clinical_impact` -- ponderer les erreurs selon leur gravite clinique.

---

## 7. Recommandations specifiques pour un benchmark base sur des guidelines

Les benchmarks bases sur des guidelines (vs. connaissances medicales generales) ont des specificites importantes :

### Ce que fait AMEGA (notre meilleure reference)

1. **Tracabilite guideline -> question** : chaque element de scoring est lie a une recommandation precise.
2. **Scoring pondere par consequence clinique** : une erreur sur la molecule d'antibioprophylaxie est plus grave qu'une erreur sur l'intervalle de reinjection.
3. **Questions nouvelles (pas d'examen existant)** : les questions sont creees de novo pour eviter le data leakage (les LLM ayant potentiellement vu les questions d'examen pendant l'entrainement).
4. **Evaluation de l'absence de reponse** : tester que le modele sait dire "pas d'antibioprophylaxie" quand c'est la bonne reponse.

### Risques specifiques

- **Data leakage** : si les RFE SFAR sont dans les donnees d'entrainement des LLM, les QCM simples ne discriminent plus. Privilegier les vignettes cliniques originales.
- **Mise a jour des guidelines** : les recommandations changent. Indiquer la version de reference et prevoir un mecanisme de mise a jour.
- **Niveau de preuve** : certaines recommandations sont des "accords d'experts" (faible preuve), d'autres des "grade A". Documenter cela par question pour interpreter les erreurs.

### Recommandation : evolution du dataset actuel

Le dataset actuel (23 questions, 14 ouvertes + 9 QCM) est un bon point de depart mais souffre de :

1. **Couverture insuffisante** : seules orthopedie programmee et traumatologie sont couvertes. Les RFE SFAR couvrent aussi la chirurgie digestive, urologique, cardiaque, ORL, etc.
2. **Scoring trop binaire** : exact match uniquement, pas de credit partiel.
3. **Absence de vignettes cliniques** : toutes les questions sont des rappels directs de la guideline.
4. **Pas de metadata de difficulte ni d'impact clinique**.

**Plan d'action propose :**

| Priorite | Action | Effort |
|----------|--------|--------|
| P0 | Ajouter `difficulty`, `clinical_impact`, `accepted_synonyms` aux 23 questions existantes | 2h |
| P1 | Creer 15-20 vignettes cliniques (scenarios realistes multi-facteurs) | 4h |
| P2 | Etendre aux autres specialites chirurgicales du RFE (digestif, uro, ORL...) | 6h |
| P3 | Ajouter des scoring rubrics multi-criteres (molecule + dose + duree) | 3h |
| P4 | Faire valider par 1-2 anesthesistes, calculer kappa | Variable |
| P5 | Ajouter des questions "pieges" (pas d'ABP, ou la reponse attendue est "Non") | 2h |

Objectif final : **60-80 questions** avec metadata complete, couvrant toutes les sections du RFE, avec mix open/QCM/vignettes et scoring multi-criteres.

---

## Sources

- [AMEGA: Autonomous Medical Evaluation for Guideline Adherence -- npj Digital Medicine](https://www.nature.com/articles/s41746-024-01356-6)
- [AMEGA GitHub](https://github.com/DATEXIS/AMEGA-benchmark/)
- [HealthBench: Evaluating LLMs Towards Improved Human Health -- OpenAI](https://openai.com/index/healthbench/)
- [HealthBench paper -- arXiv](https://arxiv.org/abs/2505.08775)
- [HealthBench dataset -- Hugging Face](https://huggingface.co/datasets/openai/healthbench)
- [MedQA benchmark](https://www.vals.ai/benchmarks/medqa)
- [PubMedQA -- ACL Anthology](https://aclanthology.org/D19-1259/)
- [Swedish Medical LLM Benchmark -- Frontiers](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full)
- [CSEDB: Safety and Effectiveness benchmark -- Nature](https://www.nature.com/articles/s41746-025-02277-8)
- [Medical LLM Benchmarks Should Prioritize Construct Validity -- arXiv](https://arxiv.org/html/2503.10694v1)
- [Knowledge-Practice Performance Gap in Clinical LLMs -- JMIR](https://www.jmir.org/2025/1/e84120/PDF)
- [MedBench v4 -- arXiv](https://arxiv.org/abs/2511.14439)
- [Open Medical-LLM Leaderboard -- Hugging Face](https://huggingface.co/blog/leaderboard-medicalllm)
- [CPGPrompt: Clinical Guidelines into LLM Decision Support -- arXiv](https://arxiv.org/pdf/2601.03475)
- [MedThink-Bench: Automating expert-level reasoning evaluation -- npj Digital Medicine](https://www.nature.com/articles/s41746-025-02208-7)
