# Recherche : Comparaison multi-approches LLM pour les guidelines medicales

Date : 2026-03-27

## Synthese

Notre benchmark compare 5+ approches (simple prompt, RAG PDF, RAG donnees structurees, long context, MCP/tools, fine-tuning, agents/skills) sur un meme jeu de questions d'antibioprophylaxie SFAR. La litterature recente (2024-2025) montre que cette comparaison "multi-approche sur une meme tache medicale" reste rare. La plupart des etudes comparent seulement 2-3 approches (typiquement RAG vs fine-tuning, ou RAG vs long context). Notre angle est donc bien differenciateur.

---

## 1. Etudes comparant RAG vs fine-tuning vs long context sur des taches medicales

### Etude cle : Medical LLMs: Fine-Tuning vs. RAG (2025)

- **Source** : [Medical LLMs: Fine-Tuning vs. Retrieval-Augmented Generation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292519/) (MDPI Bioengineering, juin 2025)
- **Protocole** : 5 modeles (Llama-3.1-8B, Gemma-2-9B, Mistral-7B-Instruct, Qwen2.5-7B, Phi-3.5-Mini) testes en 3 modes : RAG seul, fine-tuning (FT) seul, FT+RAG, sur le dataset MedQuAD.
- **Resultats** :
  - RAG et FT+RAG surpassent systematiquement FT seul sur la plupart des modeles.
  - Llama montre les meilleures performances globales ; Phi excelle en mode RAG/FT+RAG.
  - RAG offre un avantage pratique : pas besoin de donnees d'entrainement massives, mise a jour facile.

### Etude : RAG pour 10 LLMs en aptitude chirurgicale (2025)

- **Source** : [Retrieval augmented generation for 10 large language models and its generalizability in assessing medical fitness](https://www.nature.com/articles/s41746-025-01519-z) (npj Digital Medicine, 2025)
- **Protocole** : 10 LLMs avec RAG, 35 guidelines locaux + 23 internationaux, 14 scenarios cliniques d'aptitude chirurgicale.
- **Resultats** : GPT-4 LLM-RAG avec guidelines internationaux atteint 96.4% de precision vs 86.6% pour les reponses humaines (p = 0.016). RAG ameliore la precision de chaque modele de 39.7% en moyenne.

### Revue systematique et meta-analyse : RAG en biomedecine (2025)

- **Source** : [Improving large language model applications in biomedicine with RAG](https://academic.oup.com/jamia/article/32/4/605/7954485) (JAMIA, 2025)
- **Resultats** : Synthese de la litterature 2023-2024 confirmant l'efficacite du RAG en biomedicine, avec des guidelines de developpement clinique.

**Constat** : Aucune de ces etudes ne compare simultanement RAG, long context, fine-tuning, ET agents/tools sur le meme dataset medical.

---

## 2. RAG vs Long Context pour le Q&A sur les guidelines

### Etude cle : Long Context vs. RAG for LLMs (2025)

- **Source** : [Long Context vs. RAG for LLMs: An Evaluation and Revisits](https://arxiv.org/abs/2501.01880) (arXiv, janvier 2025)
- **Resultats** :
  - Long context surpasse RAG quand les ressources sont suffisantes.
  - RAG est nettement plus efficient en cout.
  - La performance de la plupart des modeles diminue apres une certaine taille de contexte (Llama-3.1-405b : au-dela de 32k tokens, GPT-4 : au-dela de 64k tokens).

### LaRA Benchmark (2025)

- **Source** : [LaRA: Benchmarking RAG and Long-Context LLMs](https://openreview.net/forum?id=CLF25dahgA) (OpenReview / ICLR, 2025)
- **Resultats** : Pas de solution universelle. Le choix depend de la taille du modele, du type de tache, de la longueur du contexte et de la qualite du retrieval.

### Implications pour notre benchmark

- Long context convient bien aux documents statiques et longs (comme les RFE SFAR).
- RAG est preferable quand les donnees sont dynamiques ou diversifiees.
- Le "brute-force" du long context degrade la qualite et augmente les couts de maniere non lineaire.

---

## 3. Approches MCP / Tool-use pour la recherche de connaissances medicales

### Etat de l'art

Le MCP (Model Context Protocol, Anthropic, novembre 2024) est trop recent pour avoir des etudes cliniques publiees comparant formellement MCP vs RAG vs fine-tuning.

### Donnees disponibles

- **Source** : [Custom Large Language Models Improve Accuracy: Comparing RAG and AI Agents](https://www.sciencedirect.com/science/article/abs/pii/S0749806324008831) (ScienceDirect, 2024)
- L'ajout d'agents IA a un LLM deja augmente par RAG fait passer GPT-4 de ~90% a 95% de precision pour les guidelines orthopediques.
- **Source** : [Agentic Medical Knowledge Graphs](https://arxiv.org/abs/2502.13010) (arXiv, 2025) : AMG-RAG atteint F1=74.1% sur MEDQA, surpassant des modeles 10-100x plus grands.

### Tool RAG

- **Source** : [Tool RAG: The Next Breakthrough in Scalable AI Agents](https://next.redhat.com/2025/11/26/tool-rag-the-next-breakthrough-in-scalable-ai-agents/) (Red Hat, 2025)
- Concept : au lieu de charger tous les outils dans le contexte, on fait du retrieval pour selectionner dynamiquement les outils pertinents.

**Constat** : Notre approche MCP/tools pour la recherche de guidelines medicales est pionniere. Aucune etude publiee ne compare formellement MCP a RAG ou long context sur une tache medicale.

---

## 4. Fine-tuning vs modeles generaux + RAG

### Consensus de la litterature

| Critere | Fine-tuning | RAG | FT + RAG |
|---|---|---|---|
| Precision | Moderee | Elevee | Maximale |
| Cout de mise en place | Eleve (donnees, compute) | Modere (index, embeddings) | Tres eleve |
| Mise a jour des connaissances | Necessite re-entrainement | Mise a jour de l'index | Complexe |
| Hallucinations | Risque eleve | Reduit (source externe) | Minimise |
| Donnees requises | ~100k exemples recommandes | Documents bruts | Les deux |

### Limites du fine-tuning medical

- **Source** : [Fine-tuning medical language models for enhanced long-contextual understanding](https://pmc.ncbi.nlm.nih.gov/articles/PMC12209640/) (PMC, 2025)
- Manque de donnees etiquetees de haute qualite en medecine.
- Ecart de distribution entre donnees d'entrainement et deploiement reel.
- Ratio optimal : 1:1 donnees generales / professionnelles, volume ~100k.

### Recommandation convergente

RAG est l'approche la plus pratique pour la majorite des cas d'usage medicaux. Le fine-tuning est reserve aux cas ou l'on dispose de grandes quantites de donnees specialisees et ou la latence est critique.

---

## 5. Metriques d'evaluation au-dela de la precision

### Metriques recommandees par la litterature

| Categorie | Metriques |
|---|---|
| **Precision** | Accuracy, F1, BERTScore, BLEURT |
| **Fidelite** | Faithfulness (RAGAS), TruthfulQA, taux d'hallucination |
| **Securite clinique** | Taux d'omission, erreurs cliniquement significatives |
| **Performance** | Latence, tokens consommes, cout par requete |
| **Raisonnement** | Efficience diagnostique, completude, precision factuelle (MedR-Bench) |
| **Methodologie avancee** | IRT 3PL (stratification de difficulte), scoring hybride expert + LLM |

### Frameworks d'evaluation medicaux (2025)

- **MedHELM** (Stanford HAI) : evaluation holistique des LLMs medicaux.
- **MedS-Bench**, **MedAgentsBench**, **MedCheck** : benchmarks multi-activites cliniques.
- **MedR-Bench** : 1453 cas patients structures, evaluation en 3 etapes (examen, diagnostic, traitement).
- **LLMEval-Med** : benchmark clinique reel avec validation par medecins.

### Sources

- [Holistic Evaluation of LLMs for Medical Applications](https://hai.stanford.edu/news/holistic-evaluation-of-large-language-models-for-medical-applications) (Stanford HAI)
- [A Brief Review on Benchmarking for LLM Evaluation in Healthcare](https://wires.onlinelibrary.wiley.com/doi/10.1002/widm.70010) (WIREs, 2025)
- [LLMEval-Med: A Real-world Clinical Benchmark](https://arxiv.org/html/2506.04078v1) (arXiv, 2025)

---

## 6. Impact de l'approche sur les hallucinations

### RAG reduit les hallucinations

- **Source** : [Evaluating RAG Variants for Clinical Decision Support: Hallucination Mitigation](https://www.mdpi.com/2079-9292/14/21/4227) (Electronics, 2025)
- Self-reflective RAG reduit les hallucinations a 5.8% dans les evaluations de decision clinique (12 variantes de RAG testees sur 250 vignettes patients).

- **Source** : [Framework to assess clinical safety and hallucination rates of LLMs](https://www.nature.com/articles/s41746-025-01670-7) (npj Digital Medicine, 2025)
- Taux d'hallucination observe : 1.47%, taux d'omission : 3.45% (sur 12 999 phrases annotees par des cliniciens).

### MEGA-RAG pour la sante publique

- **Source** : [MEGA-RAG: multi-evidence guided answer refinement](https://pmc.ncbi.nlm.nih.gov/articles/PMC12540348/) (Frontiers in Public Health, 2025)
- Framework multi-evidence pour attenuer les hallucinations en sante publique.

### Risques persistants

- RAG peut introduire des erreurs si le retrieval retourne des informations non pertinentes ou de mauvaise qualite.
- Le conflit retrieval-generation survient quand les documents recuperes contredisent les connaissances parametriques du modele.
- Les attaques adversariales peuvent augmenter significativement les taux d'hallucination.

---

## 7. Donnees structurees vs non structurees dans le RAG medical

### Consensus

- Les systemes RAG medicaux optimaux integrent les deux types de donnees (structurees et non structurees).
- Les graphes de connaissances (knowledge graphs) ameliorent la precision et la pertinence clinique mais souffrent de connaissances statiques.
- **Source** : [Medical Graph RAG](https://aclanthology.org/2025.acl-long.1381.pdf) (ACL, 2025) : approche evidence-based combinant graphes et RAG.

### Implications pour notre benchmark

Notre comparaison RAG-PDF vs RAG-Excel est pertinente et peu etudiee dans la litterature. La question de l'impact du format source (PDF non structure vs donnees tabulaires structurees) sur la qualite du retrieval et les hallucinations est un angle original.

---

## 8. Recommandations pour notre benchmark

### Positionnement

Notre benchmark est **unique** sur plusieurs axes :
1. **Nombre d'approches comparees** (5+) : la litterature compare typiquement 2-3 approches.
2. **Inclusion du MCP/tools** : aucune etude publiee ne compare formellement MCP a d'autres approches sur une tache medicale.
3. **RAG-PDF vs RAG-structure** : angle peu explore, pertinent pour les guidelines medicales.
4. **Application specifique** : antibioprophylaxie chirurgicale (RFE SFAR 2024), pas de travaux existants sur ce sujet avec des LLMs.

### Metriques a adopter

En plus de nos metriques actuelles (precision, latence, cout, tokens), considerer :
- **Taux d'hallucination** : annoter manuellement un sous-ensemble de reponses.
- **Faithfulness** : utiliser RAGAS ou un score de fidelite a la source.
- **Taux d'omission** : informations critiques manquantes dans la reponse.
- **Scoring hybride** : combiner evaluation automatique (LLM-as-judge) et validation clinicienne.

### Resultats attendus (hypotheses basees sur la litterature)

1. RAG (PDF et Excel) > Simple prompt en precision.
2. RAG-Excel >= RAG-PDF (donnees structurees facilitent le retrieval).
3. Long context competitif avec RAG pour les documents courts (~30 pages des RFE SFAR).
4. MCP/tools potentiellement superieur grace a la capacite d'utiliser des fonctions specifiques.
5. Fine-tuning seul < RAG, sauf si combine avec RAG.
6. Agent/skills : gain marginal si la tache reste simple (lookup), gain potentiel pour les questions complexes multi-etapes.

### Lacunes a exploiter dans les publications

- Aucune etude ne compare toutes ces approches sur un meme jeu de donnees medical.
- Le MCP pour les guidelines medicales est un territoire vierge.
- L'impact du format source (PDF vs tabulaire) sur le RAG medical est sous-etudie.
- Les metriques de cout et d'emissions CO2 sont rarement rapportees.

---

## Sources principales

- [Medical LLMs: Fine-Tuning vs. RAG](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292519/) - MDPI Bioengineering, 2025
- [RAG for 10 LLMs in assessing medical fitness](https://www.nature.com/articles/s41746-025-01519-z) - npj Digital Medicine, 2025
- [Long Context vs. RAG for LLMs](https://arxiv.org/abs/2501.01880) - arXiv, 2025
- [LaRA: Benchmarking RAG and Long-Context LLMs](https://openreview.net/forum?id=CLF25dahgA) - OpenReview, 2025
- [Improving LLM applications in biomedicine with RAG](https://academic.oup.com/jamia/article/32/4/605/7954485) - JAMIA, 2025
- [Custom LLMs: Comparing RAG and AI Agents](https://www.sciencedirect.com/science/article/abs/pii/S0749806324008831) - ScienceDirect, 2024
- [Agentic Medical Knowledge Graphs](https://arxiv.org/abs/2502.13010) - arXiv, 2025
- [RAG Variants for Clinical Decision Support: Hallucination Mitigation](https://www.mdpi.com/2079-9292/14/21/4227) - Electronics, 2025
- [Framework for clinical safety and hallucination rates](https://www.nature.com/articles/s41746-025-01670-7) - npj Digital Medicine, 2025
- [Fine-tuning medical LLMs for long-contextual understanding](https://pmc.ncbi.nlm.nih.gov/articles/PMC12209640/) - PMC, 2025
- [Holistic Evaluation of LLMs for Medical Applications](https://hai.stanford.edu/news/holistic-evaluation-of-large-language-models-for-medical-applications) - Stanford HAI
- [Benchmarking for LLM Evaluation in Healthcare](https://wires.onlinelibrary.wiley.com/doi/10.1002/widm.70010) - WIREs, 2025
- [MEGA-RAG for public health](https://pmc.ncbi.nlm.nih.gov/articles/PMC12540348/) - Frontiers, 2025
- [Medical Graph RAG](https://aclanthology.org/2025.acl-long.1381.pdf) - ACL, 2025
- [Development and evaluation of agentic LLM-based RAG](https://pmc.ncbi.nlm.nih.gov/articles/PMC12306375/) - PMC, 2025
- [Tool RAG for scalable AI agents](https://next.redhat.com/2025/11/26/tool-rag-the-next-breakthrough-in-scalable-ai-agents/) - Red Hat, 2025
- [RAG in Healthcare: A Comprehensive Review](https://www.mdpi.com/2673-2688/6/9/226) - MDPI, 2025
