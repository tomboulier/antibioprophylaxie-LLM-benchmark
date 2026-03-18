# Comparaison des cadres d'évaluation LLM existants

Date : 2026-03-17
Contexte : évaluation avant implémentation de `medical-llm-benchmark`

## Cadres évalués

### 1. lm-evaluation-harness (EleutherAI)

**URL :** https://github.com/EleutherAI/lm-evaluation-harness

**Ce que c'est :** cadre d'évaluation académique, backend du leaderboard HuggingFace Open LLM. Supporte 60+ benchmarks standardisés.

**Points forts :**
- Très mature, utilisé par NVIDIA, Cohere, BigScience, etc.
- Support natif HuggingFace, vLLM, SGLang
- Configuration des tâches via YAML
- Reproductibilité garantie (prompts publics)

**Limites pour notre contexte :**
- Orienté modèles open-source locaux (HuggingFace/vLLM) — support API commercial limité
- Pas de notion d'*approche* (RAG vs contexte long vs MCP)
- Ajouter un jeu de données médical custom en français demande de maîtriser leur système de tâches YAML — non trivial
- Pas de métriques d'empreinte carbone

**Verdict :** trop orienté recherche académique et modèles locaux pour notre cas d'usage.

---

### 2. openai/evals

**URL :** https://github.com/openai/evals

**Ce que c'est :** cadre d'évaluation d'OpenAI, avec un registre public de benchmarks.

**Points forts :**
- Simple à utiliser pour des evals basiques (JSON + YAML)
- Intégration native OpenAI Dashboard

**Limites pour notre contexte :**
- Centré OpenAI — pas multi-providers
- Code custom non accepté dans les contributions
- Peu maintenu activement depuis 2023
- Pas de notion d'approche, pas de métriques opérationnelles

**Verdict :** trop limité et trop lié à OpenAI.

---

### 3. DeepEval (confident-ai)

**URL :** https://github.com/confident-ai/deepeval

**Ce que c'est :** cadre d'évaluation orienté applications LLM (RAG, agents, chatbots). Fonctionne comme pytest pour les LLM.

**Points forts :**
- Support multi-providers via API
- Métriques RAG prêtes à l'emploi (faithfulness, answer relevancy, contextual recall)
- Extensible, proche de pytest
- LLM-as-a-judge pour évaluation sémantique

**Limites pour notre contexte :**
- Scoring via LLM-as-a-judge : coûteux, non déterministe, moins reproductible
- Pas de scoring médical spécifique (multi-molécules, QCM en français, sourçage RFE)
- Pas de métriques d'empreinte carbone
- Pas de notion d'approche comme dimension de comparaison

**Verdict :** le plus proche de notre besoin, mais le LLM-as-a-judge contredit notre exigence de déterminisme (R4). Pourrait servir de scorer optionnel pour l'évaluation sémantique dans une version future.

---

## LiteLLM — retenu comme adaptateur LLM

**URL :** https://github.com/BerriAI/litellm

**Ce que c'est :** proxy unifié pour 100+ providers LLM (Anthropic, OpenAI, Mistral, Cohere, etc.) via une interface unique.

**Pourquoi on l'utilise :**
- Évite d'implémenter un adaptateur par provider
- Gère retry, timeout, rate limiting
- Interface identique quel que soit le provider
- S'intègre proprement derrière notre `LLMPort` (un seul `LiteLLMAdapter`)

---

## Décision d'architecture

On implémente `medical-llm-benchmark` from scratch pour les raisons suivantes :

1. **Scoring déterministe** : aucun framework existant ne connaît les règles métier SFAR (multi-molécules, QCM en français, sourçage de RFE)
2. **Notion d'approche** : la comparaison RAG vs contexte long vs MCP n'existe dans aucun de ces frameworks
3. **Empreinte carbone** : non couverte par ces frameworks
4. **Public cible** : sociétés savantes médicales — besoin de reproductibilité et de lisibilité, pas de LLM-as-a-judge

On réutilise LiteLLM pour la couche d'appel aux APIs LLM afin de ne pas réinventer la roue sur la gestion des providers.
