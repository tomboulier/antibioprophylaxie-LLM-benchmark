# Strategie de publication -- Benchmark LLM antibioprophylaxie SFAR

*Recherche effectuee le 27 mars 2026*

---

## 1. Revues et conferences cibles

### Tier 1 -- Revues a fort impact (IF > 10)

| Revue | IF | Angle adapte | Notes |
|---|---|---|---|
| **npj Digital Medicine** (Nature) | ~15 | Framework + resultats cliniques | AMEGA y a ete publie (dec. 2024). Call for papers "Evaluating Real-World Clinical Performance of AI" ouvert, **deadline 16 juillet 2026** (pas 3 juin). |
| **NEJM AI** | nouveau | Clinical reasoning benchmark | Publie des etudes de benchmark clinique (ex: clinical reasoning assessment, 2025). Tres selectif. |
| **Nature Medicine** | ~87 | Resultats a fort impact clinique | Publie des etudes LLM medicales mais exige un impact clinique demonstre. Pas ideal pour un benchmark seul. |

### Tier 2 -- Revues d'informatique medicale (IF 3-10)

| Revue | IF | Angle adapte | Notes |
|---|---|---|---|
| **JAMIA** (J Am Med Inform Assoc) | ~7 | Framework d'evaluation + methodologie | Publie regulierement des travaux sur l'evaluation de LLM en contexte clinique. |
| **JBI** (J Biomedical Informatics) | ~4 | Benchmark multilingue / methodologie NLP | Special issue en cours: "Biomedical Multimodal LLMs" (verifier deadline). |
| **JMIR** / **JMIR Medical Informatics** | ~5 / ~3 | Evaluation LLM en contexte clinique | Publie des etudes de benchmarking (ex: confiance des LLM, 2025). Processus rapide. |
| **BMC Medical Informatics** | ~3 | Revue systematique + benchmark | A publie une revue systematique de 39 benchmarks LLM cliniques (2025). |

### Tier 3 -- Revues open-access / specialisees

| Revue | IF | Angle adapte | Notes |
|---|---|---|---|
| **Frontiers in AI** | ~3 | Framework benchmark specifique a une langue | Le Swedish Medical LLM Benchmark (SMLB) y a ete publie (2025). Excellent precedent pour notre angle "benchmark francophone". |
| **Artificial Intelligence in Medicine** | ~7 | Methodologie IA medicale | Historiquement forte sur les benchmarks. |
| **JMIR AI** | nouveau | Evaluation LLM clinique | A publie "Clinical LLM Evaluation by Expert Review" (2025). |

### Conferences

| Conference | Dates | Angle | Notes |
|---|---|---|---|
| **SFAR 2026** | 16-18 sept 2026 | Application clinique antibioprophylaxie | **Abstract deadline: 21 avril 2026.** Angle: "un outil IA pour les RFE". |
| **ML4H** (Machine Learning for Health) | dec 2026 (avant NeurIPS) | Benchmark + framework technique | Symposium independant. Accepte des "findings papers" et "datasets". |
| **MICCAI workshops** | sept 2026 | Clinical MLLMs | Workshop "Clinical MLLMs" en 2025. Verifier l'edition 2026. |
| **AIME** (AI in Medicine Europe) | 2026 TBD | Framework d'evaluation | Conference europeenne, bon fit thematique. |
| **CHIL** (Conference on Health, Inference, Learning) | 2026 TBD | Methodologie de benchmark | Accepte des travaux techniques sur l'evaluation en sante. |

### Revues pour un data paper (dataset seul)

| Revue | Angle | Notes |
|---|---|---|
| **Scientific Data** (Nature) | Dataset SFAR antibioprophylaxie Q&A | Revue dediee aux descriptions de datasets. Exige depot dans un repository (HuggingFace convient). |
| **Data in Brief** (Elsevier) | Dataset + description | Publication rapide. FAIR-compliant. |
| **JMIR Data** | Dataset medical | Specialise dans les datasets de sante numerique. |

---

## 2. Ce qui rend un benchmark medical publiable

D'apres l'analyse des papiers publies et des criteres recenses (notamment "Medical LLM Benchmarks Should Prioritize Construct Validity", arXiv 2503.10694):

### Criteres essentiels

1. **Validite de construit (construct validity)** -- Le benchmark mesure-t-il reellement la competence clinique qu'il pretend evaluer? C'est le critere n1 selon les reviewers en 2025.

2. **Validation par des experts** -- Les questions doivent etre creees ou validees par des cliniciens. HealthBench: 262 medecins. AMEGA: experts de 13 specialites. Notre projet doit documenter la validation par des anesthesistes/infectiologues.

3. **Representativite clinique** -- Pas que du QCM. Les reviewers veulent des scenarios realistes, ouverts, proches de la pratique. L'utilisation de questions ouvertes (pas uniquement multiple choice) est un avantage.

4. **Scoring rigoureux** -- Aller au-dela de la simple exactitude. AMEGA utilise un scoring pondere (1337 elements). HealthBench utilise des rubrics multi-criteres. Documenter precision, rappel, et un schema de scoring cliniquement pertinent.

5. **Reproductibilite** -- Code ouvert, dataset accessible, parametres des modeles documentes (temperature, prompts, nombre d'essais).

6. **Comparaison multi-modeles** -- Tester au moins 5-10 modeles, incluant des modeles ouverts et proprietaires.

7. **Analyse des erreurs** -- Les reviewers attendent une analyse qualitative des erreurs, pas seulement des scores agrreges.

8. **Securite et ethique** -- Evaluer les risques (hallucinations dangereuses, biais). Documenter les implications cliniques des erreurs.

### Criteres differenciants (pour les meilleures revues)

- Evaluation multi-approches (RAG, long context, fine-tuning, MCP) -- c'est notre force
- Benchmark dans une langue non anglaise -- angle sous-exploite
- Lien avec des guidelines officielles (RFE SFAR) -- ancrage clinique fort
- Framework extensible a d'autres specialites -- valeur ajoutee technique

---

## 3. Publication du dataset separement

### Strategie recommandee: double publication

**Oui, c'est faisable et courant.** Strategie en deux temps:

1. **Data paper** dans Scientific Data, Data in Brief, ou JMIR Data
   - Decrit le dataset (questions, reponses attendues, schema de scoring)
   - Depose sur HuggingFace Hub avec DOI (via Zenodo ou directement HuggingFace)
   - Peut etre publie avant ou en parallele du papier de benchmark

2. **Papier de benchmark** dans une revue informatique medicale
   - Cite le data paper pour le dataset
   - Se concentre sur la methodologie d'evaluation et les resultats

### Precedents

- **HealthBench**: dataset sur HuggingFace (`openai/healthbench`), papier sur arXiv
- **MedQA**: dataset sur HuggingFace, papier dans un workshop
- **SMLB**: code sur GitHub, papier dans Frontiers in AI
- **AMEGA**: code sur GitHub (`DATEXIS/AMEGA-benchmark`), papier dans npj Digital Medicine

### Recommandation pour le depot

- Depot principal: **HuggingFace Hub** (visibilite maximale dans la communaute ML)
- DOI persistant: **Zenodo** (citabilite academique)
- Code: **GitHub** avec licence ouverte (Apache 2.0 ou MIT)

---

## 4. Structure type d'un papier de benchmark medical

D'apres l'analyse de AMEGA (npj Digital Medicine), SMLB (Frontiers in AI), HealthBench (arXiv), et MedExpQA (Artificial Intelligence in Medicine):

### Structure standard

```
1. Introduction
   - Contexte: LLM en medecine, besoin d'evaluation rigoureuse
   - Gap: manque de benchmarks [francophones / pour les guidelines / multi-approches]
   - Contribution: resume en 3-4 bullet points

2. Related Work
   - Benchmarks medicaux existants (MedQA, USMLE, PubMedQA, etc.)
   - Evaluation de LLM en contexte clinique
   - Specificites linguistiques / culturelles si applicable

3. Benchmark Design
   3.1 Source des donnees (RFE SFAR 2024)
   3.2 Construction du dataset (processus, validation par experts)
   3.3 Taxonomie des questions (types, difficulte, specialite)
   3.4 Schema de scoring (metriques, ponderation)

4. Experimental Setup
   4.1 Modeles evalues (liste, parametres)
   4.2 Approches testees (RAG, long context, fine-tuning, MCP)
   4.3 Infrastructure et configuration
   4.4 Metriques (precision, latence, cout, emissions CO2)

5. Results
   5.1 Performance globale (tableau comparatif)
   5.2 Analyse par type de question
   5.3 Analyse par approche
   5.4 Analyse des erreurs (exemples, categories)
   5.5 Cout et performance (trade-off)

6. Discussion
   - Implications cliniques
   - Limites (taille du dataset, scope, biais potentiels)
   - Comparaison avec d'autres benchmarks
   - Extensibilite du framework

7. Conclusion
   - Recommandations pour l'utilisation clinique
   - Directions futures (autres specialites, autres langues)

Supplementary Materials
   - Dataset complet (lien HuggingFace)
   - Code de benchmark (lien GitHub)
   - Resultats detailles par question
```

---

## 5. Venues francophones

| Venue | Type | Pertinence | Notes |
|---|---|---|---|
| **SFAR congres** | Conference | Tres forte | Public cible direct (anesthesistes). Abstract = communication courte. |
| **JFIM** (Journees Francophones d'Informatique Medicale) | Conference | Forte | Communaute francophone d'informatique medicale. Tenu tous les 2 ans. Verifier calendrier 2026. |
| **IRBM** (Innovation and Research in BioMedical engineering) | Revue | Moyenne | Revue franco-europeenne en ingenierie biomedicale. |
| **Annales Francaises d'Anesthesie et de Reanimation** | Revue | Forte | Revue de la SFAR. Angle clinique, pas technique. |
| **Revue d'Epidemiologie et de Sante Publique** | Revue | Faible | Seulement si angle sante publique. |

---

## 6. Analyse des publications de reference

### AMEGA (npj Digital Medicine, dec. 2024)
- **Angle**: evaluation autonome de l'adherence aux guidelines medicales
- **Forces**: 20 scenarios diagnostiques, 13 specialites, 17 modeles testes, scoring pondere (1337 elements)
- **Lecon**: l'ancrage dans les guidelines officielles (comme nos RFE SFAR) est un differenciateur fort
- **[Lien](https://www.nature.com/articles/s41746-024-01356-6)**

### HealthBench (arXiv, mai 2025)
- **Angle**: evaluation a grande echelle (5000 conversations, 262 medecins)
- **Forces**: scenarios multi-tours, rubrics validees par consensus medical, open source
- **Lecon**: la validation par un grand nombre de medecins renforce enormement la credibilite
- **[Lien](https://arxiv.org/abs/2505.08775)** | **[Dataset HuggingFace](https://huggingface.co/datasets/openai/healthbench)**

### SMLB (Frontiers in AI, 2025)
- **Angle**: benchmark specifique a une langue (suedois)
- **Forces**: 4 datasets, 18 modeles, framework extensible, open source
- **Lecon**: **precedent direct pour notre projet.** Un benchmark dans une langue non anglaise a ete publie dans Frontiers in AI. Notre angle "benchmark francophone" est viable.
- **[Lien](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full)**

---

## 7. Calendrier et recommandations

### Timeline proposee

| Date | Action | Cible |
|---|---|---|
| **Avant 21 avril 2026** | Soumettre un abstract au congres SFAR 2026 | SFAR 2026 |
| **Avant 11 mai 2026** | Soumettre un dossier AMI BOAS (si le framework rentre dans les criteres HDH) | AMI BOAS edition 10 |
| **Mai-juin 2026** | Deposer le dataset sur HuggingFace + Zenodo | Open data |
| **Avant 16 juillet 2026** | Soumettre le papier principal a npj Digital Medicine (collection "Real-World Clinical Performance of AI") | npj Digital Medicine |
| **Juillet 2026 (backup)** | Si npj trop ambitieux: soumettre a Frontiers in AI ou JMIR Medical Informatics | Frontiers / JMIR |
| **Sept 2026** | Presenter au congres SFAR (si abstract accepte) | SFAR 2026 |
| **Oct-nov 2026** | Soumettre un data paper a Scientific Data ou JMIR Data | Data paper |
| **Dec 2026** | Soumettre a ML4H (findings paper) si les resultats sont prets | ML4H 2026 |

### Strategie multi-publication recommandee

1. **Abstract SFAR** (priorite immediate) -- Communication courte, angle clinique: "Comment l'IA peut-elle aider a consulter les RFE d'antibioprophylaxie?"

2. **Papier principal** (npj Digital Medicine ou Frontiers in AI) -- Benchmark complet: 5 approches, multi-modeles, scoring expert, framework extensible. S'inspirer de SMLB pour l'angle "benchmark francophone" et d'AMEGA pour l'angle "guideline adherence".

3. **Data paper** (Scientific Data ou JMIR Data) -- Dataset seul, FAIR, avec documentation detaillee.

4. **AMI BOAS** (si eligible) -- Le framework open source + les algorithmes de scoring pourraient rentrer dans le scope BOAS. A verifier lors du webinaire du 1er avril 2026.

### Differenciateurs a mettre en avant

- **Premier benchmark francophone** sur les guidelines medicales (pas de concurrent direct)
- **Comparaison multi-approches** (RAG, long context, fine-tuning, MCP) -- unique par rapport a AMEGA/HealthBench qui ne testent que des modeles bruts
- **Ancrage dans des guidelines officielles** (RFE SFAR 2024) -- validite clinique forte
- **Framework extensible** -- applicable a d'autres societes savantes
- **Metriques holistiques** -- precision, latence, cout, emissions CO2

---

## Sources

- [AMEGA -- npj Digital Medicine (2024)](https://www.nature.com/articles/s41746-024-01356-6)
- [HealthBench -- arXiv (2025)](https://arxiv.org/abs/2505.08775)
- [HealthBench dataset -- HuggingFace](https://huggingface.co/datasets/openai/healthbench)
- [SMLB -- Frontiers in AI (2025)](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full)
- [npj Digital Medicine -- Calls for papers](https://www.nature.com/npjdigitalmed/calls-for-papers)
- [npj Digital Medicine -- Collection "Evaluating Real-World Clinical Performance of AI"](https://www.nature.com/collections/hcdeibadid)
- [Medical LLM Benchmarks Should Prioritize Construct Validity (arXiv 2503.10694)](https://arxiv.org/pdf/2503.10694)
- [NEJM AI -- Clinical Reasoning Benchmark (2025)](https://ai.nejm.org/doi/full/10.1056/AIdbp2500120)
- [JMIR Medical Informatics -- LLM Confidence Benchmarking (2025)](https://medinform.jmir.org/2025/1/e66917)
- [BMC Medical Informatics -- Systematic Review of LLM Evaluations (2025)](https://link.springer.com/article/10.1186/s12911-025-02954-4)
- [JBI -- Special Issue on Biomedical Multimodal LLMs](https://www.sciencedirect.com/special-issue/313351/special-issue-on-biomedical-multimodal-large-language-models-novel-approaches-and-applications)
- [Scientific Data (Nature)](https://www.nature.com/sdata/)
- [Data in Brief (Elsevier)](https://www.sciencedirect.com/journal/data-in-brief)
- [JMIR Data](https://data.jmir.org/)
- [AMI BOAS -- Health Data Hub](https://www.health-data-hub.fr/ami-boas)
- [AMI BOAS edition 10 -- appelsprojetsrecherche.fr](https://www.appelsprojetsrecherche.fr/appel/8-hdh00-29489229-003)
- [AMEGA GitHub](https://github.com/DATEXIS/AMEGA-benchmark/)
- [SMLB GitHub](https://github.com/BirgerMoell/swedish-medical-benchmark/)
- [ML4H Call for Papers](https://ahli.cc/ml4h/call-for-papers/)
- [JFIM -- IMIA Francophone SIG](https://francophonesig.wordpress.com/jfim/)
- [AIME 2025](https://aime25.aimedicine.info/)
