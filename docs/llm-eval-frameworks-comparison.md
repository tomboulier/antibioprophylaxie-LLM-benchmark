# Comparaison des cadres d'évaluation LLM existants

Date initiale : 2026-03-17  
Mise à jour : 2026-03-24 (recherche approfondie panorama, angle "framework de benchmark sur guidelines de sociétés savantes")

## Contexte

Ce document évalue ce qui existe dans le domaine de l'évaluation de LLMs appliquée aux recommandations médicales de sociétés savantes, pour situer `medical-llm-benchmark` dans le paysage existant.

---

## 1. Frameworks de benchmark LLM médicaux orientés guidelines

### AMEGA — **LE plus proche** ⭐⭐⭐⭐

**URL :** https://github.com/DATEXIS/AMEGA-benchmark/  
**Paper :** npj Digital Medicine, déc. 2024

**Ce que c'est :** Framework open source d'évaluation de LLMs sur des guidelines médicales. 24 scénarios cliniques, 13 spécialités, 163 questions, 1 497 critères d'évaluation élaborés par des spécialistes. Questions ouvertes (pas seulement MCQ). Scoring automatisé par LLM-as-judge.

**Points communs avec medical-llm-benchmark :**
- Orienté guidelines médicales comme ground truth
- Questions construites par des cliniciens spécialistes
- Objectif de comparaison multi-modèles

**Limites vs notre approche :**
- Généraliste : 13 spécialités internationales, pas ciblé une société savante précise
- Guidelines non versionnées/datées (pas de RFE datée avec version)
- Pas de notion d'*approche* (RAG vs contexte long vs MCP) — un seul mode d'interrogation
- Pas de métriques opérationnelles (latence, coût, empreinte carbone)
- Scoring via LLM-as-judge = non déterministe, coûteux, moins reproductible
- Pas de positionnement "outil d'audit pour les sociétés savantes elles-mêmes"

**Verdict :** Concurrent direct le plus sérieux, mais notre architecture port/adaptateur, nos métriques opérationnelles, notre scoring déterministe et notre angle "société savante comme auditeur" nous différencient significativement.

---

### HealthBench (OpenAI) ⭐⭐⭐

**URL :** https://openai.com/index/healthbench/  
**Dataset :** https://huggingface.co/datasets/openai/healthbench

**Ce que c'est :** 5 000 conversations multi-tour sur des sujets médicaux, construites avec 262 médecins couvrant 26 spécialités. Rubrics détaillés par conversation.

**Limites :** Généraliste, pas orienté guidelines de société savante précise. Construit par OpenAI pour évaluer leurs propres modèles.

---

### CSEDB — Clinical Safety-Effectiveness Dual-Track Benchmark ⭐⭐

**Paper :** npj Digital Medicine, déc. 2025

**Ce que c'est :** Benchmark chinois, 30 métriques, 26 spécialités, évalue guideline adherence + medication safety + scoring pondéré.

**Limites :** Source chinoise, fermé, pas d'architecture extensible.

---

### Swedish Medical LLM Benchmark (SMLB) ⭐⭐

**Paper :** Frontiers in AI, juin 2025

**Ce que c'est :** 4 datasets en suédois (PubMedQA traduit, examens suédois, urgences, médecine générale). Intéressant par l'angle "national + langue non anglaise" — exactement comme nous pour le français.

---

## 2. Frameworks d'évaluation généralistes (adaptables)

### lm-evaluation-harness (EleutherAI)

**URL :** https://github.com/EleutherAI/lm-evaluation-harness

**Ce que c'est :** Cadre d'évaluation académique, backend du leaderboard HuggingFace Open LLM. 60+ benchmarks standardisés.

**Points forts :** Très mature, reproductibilité garantie, support HuggingFace natif.

**Limites pour notre contexte :**
- Orienté modèles open-source locaux (HuggingFace/vLLM) — support API commercial limité
- Pas de notion d'*approche* (RAG vs contexte long vs MCP)
- Ajouter un jeu de données médical custom en français demande de maîtriser leur système de tâches YAML — non trivial
- Pas de métriques d'empreinte carbone

**Verdict :** Trop orienté recherche académique et modèles locaux.

---

### openai/evals

**URL :** https://github.com/openai/evals

**Ce que c'est :** Cadre d'évaluation d'OpenAI, avec un registre public de benchmarks.

**Limites :** Centré OpenAI, pas multi-providers, peu maintenu depuis 2023, pas de notion d'approche ni de métriques opérationnelles.

**Verdict :** Trop limité et trop lié à OpenAI.

---

### DeepEval (confident-ai)

**URL :** https://github.com/confident-ai/deepeval

**Ce que c'est :** Cadre d'évaluation orienté applications LLM (RAG, agents, chatbots). Fonctionne comme pytest pour les LLM.

**Points forts :** Support multi-providers, métriques RAG prêtes à l'emploi, extensible.

**Limites pour notre contexte :**
- Scoring via LLM-as-a-judge : coûteux, non déterministe, moins reproductible
- Pas de scoring médical spécifique (multi-molécules, QCM en français, sourçage RFE)
- Pas de métriques d'empreinte carbone
- Pas de notion d'approche comme dimension de comparaison

**Verdict :** Le plus proche parmi les outils généralistes, mais le LLM-as-a-judge contredit notre exigence de déterminisme (R4). Pourrait servir de scorer optionnel pour l'évaluation sémantique dans une version future.

---

### Giskard (OSS + Hub)

**URL :** https://github.com/Giskard-AI/giskard-oss

**Ce que c'est :** Testing et red teaming de LLMs. Scan automatique de vulnérabilités (hallucinations, biais, prompt injection). Ont publié PHARE (benchmark multilingual, Paris AI Summit fév. 2025, avec Google DeepMind).

**Cas d'usage santé documentés :** Généraliste — aucun partenariat avec une société savante médicale, aucun dataset médical dédié.

**Verdict :** Outil complémentaire potentiel (tester la robustesse/sécurité des réponses), mais ne se chevauche pas avec notre objectif. Giskard teste "est-ce que le LLM dit des choses dangereuses ?" ; nous testons "est-ce que le LLM connaît les RFEs SFAR ?".

---

### RAGAS / LangSmith / Promptfoo / Braintrust

Outils de monitoring, testing RAG ou red teaming généralistes. Aucun n'est conçu pour évaluer la conformité à des recommandations officielles et datées d'une société savante. Non retenus.

---

## 3. Datasets existants — études ponctuelles dans la même veine

Ces travaux sont des études ponctuelles (pas des frameworks réutilisables) qui utilisent la même démarche que nous :

| Étude | Société savante / Guidelines | Dataset | Lien |
|-------|------------------------------|---------|------|
| ESC AF Guidelines (Scientific Reports, mai 2025) | ESC, guidelines FA 2024 | 30 questions | https://www.nature.com/articles/s41598-025-04309-5 |
| AAOS OA Guidelines (npj DM, fév. 2024) | American Academy of Orthopedic Surgeons | Questions sur CPGs, test consistance LLM | https://www.nature.com/articles/s41746-024-01029-4 |
| IE Prophylaxis LLM Study (PubMed, oct. 2024) | Guidelines endocardite infectieuse (dentisterie) | Accuracy LLMs sur antibioprophylaxie cardio-dentaire | https://pubmed.ncbi.nlm.nih.gov/39395898/ |
| Gosta Labs / ESMO NSCLC (ASCO 2024) | ESMO + NCCN, oncologie | Guidelines NSCLC, précision 76,9% ESMO vs 25% NCCN | https://www.gostalabs.com/news/gosta-asco-2024 |
| RAG VHC guidelines EASL (npj DM, 2024) | EASL, hépatite C | GPT-4 Turbo + RAG + prompt engineering | https://www.nature.com/articles/s41746-024-01091-y |

**Constat :** Toutes ces études *utilisent* les guidelines comme ground truth pour évaluer des LLMs, mais aucune ne produit un **framework réutilisable et extensible** à d'autres sociétés savantes. Et aucune n'est en français.

---

## 4. Côté institutionnel FR/EU

| Institution | Projet | Rapport avec notre domaine |
|-------------|--------|---------------------------|
| HAS | Cadre DMN (depuis sept. 2025) | Travaux en cours sur l'évaluation des dispositifs médicaux numériques — pas encore de référentiel LLMs |
| HDH | Projet PARTAGES (France 2030) | Production de LLMs médicaux français — pas un outil d'évaluation |
| ANS | Référentiel maturité numérique | Évaluation organisationnelle, pas LLMs |
| EU AI Act | Art. 10/40 | Exigences de test pour systèmes IA à haut risque — pas de benchmark guidelines |

---

## 5. LiteLLM — retenu comme adaptateur LLM

**URL :** https://github.com/BerriAI/litellm

**Ce que c'est :** Proxy unifié pour 100+ providers LLM (Anthropic, OpenAI, Mistral, Cohere, etc.) via une interface unique.

**Pourquoi on l'utilise :**
- Évite d'implémenter un adaptateur par provider
- Gère retry, timeout, rate limiting
- Interface identique quel que soit le provider
- S'intègre proprement derrière notre `LLMPort` (un seul `LiteLLMAdapter`)

---

## 6. Décision d'architecture

On implémente `medical-llm-benchmark` from scratch pour les raisons suivantes :

1. **Scoring déterministe** : aucun framework existant ne connaît les règles métier SFAR (multi-molécules, QCM en français, sourçage de RFE)
2. **Notion d'approche** : la comparaison RAG vs contexte long vs MCP n'existe dans aucun de ces frameworks
3. **Empreinte carbone** : non couverte par ces frameworks
4. **Public cible** : sociétés savantes médicales — besoin de reproductibilité et de lisibilité, pas de LLM-as-a-judge
5. **Architecture extensible** : port/adaptateur permet à n'importe quelle startup d'implémenter son propre adaptateur et d'être évaluée de manière standard

On réutilise LiteLLM pour la couche d'appel aux APIs LLM afin de ne pas réinventer la roue sur la gestion des providers.

---

## 7. Positionnement différenciant

| Ce que medical-llm-benchmark fait | Ce qui existe |
|---|---|
| Framework **réutilisable** (pas juste une étude ponctuelle) | Études ponctuelles (ESC FA, AAOS, antibioprophylaxie dentaire) |
| Ciblé **société savante précise + RFE datée et versionnée** | Frameworks généralistes (AMEGA : 13 spécialités) |
| **Métriques opérationnelles** : coût, latence, empreinte carbone | Aucun framework existant ne les collecte |
| **En français**, pour praticiens francophones | Tout l'existant est anglophone |
| **Dataset open source** sous licence libre | La plupart des datasets sont fermés ou non publiés |
| Architecture **port/adaptateur** : extensible par n'importe quelle startup | Pas de framework multi-approche open source |
| Outil d'**audit pour les sociétés savantes elles-mêmes** | Positionnement inexistant dans la littérature |
| **Double valeur** : benchmark publiable + framework réutilisable | Ces deux aspects sont toujours séparés dans l'existant |
