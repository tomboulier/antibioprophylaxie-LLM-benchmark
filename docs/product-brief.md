# Product Brief : medical-llm-benchmark

**Date :** 2026-03-27
**Auteur :** Thomas Boulier
**Statut :** Draft
**Version :** 1.0

---

## 1. Résumé exécutif

Framework open source d'évaluation scientifique permettant de mesurer l'alignement des LLMs aux recommandations formalisées d'experts (RFEs) publiées par les sociétés savantes médicales. Le premier cas d'usage porte sur l'antibioprophylaxie chirurgicale (RFE SFAR 2024), avec une architecture conçue pour s'étendre à d'autres RFEs (anticoagulants, etc.).

**Points clés :**
- Problème : aucun outil ne permet d'auditer objectivement si un produit à base de LLM est aligné sur les recommandations officielles d'une société savante
- Solution : un framework de benchmark avec dataset de questions validé par des experts, scoring déterministe, et métriques opérationnelles (coût, latence, empreinte carbone)
- Utilisateurs cibles : chercheurs, médecins, sociétés savantes, startups santé
- Ambition : publications scientifiques + framework réutilisable en open source

---

## 2. Problème

### Le problème

Les sociétés savantes médicales publient des recommandations formalisées d'experts (RFEs) qui sont la référence pour la pratique clinique. Des startups proposent des produits à base de LLM pour assister les praticiens, mais il n'existe aucun moyen standardisé de vérifier que ces produits sont alignés sur les RFEs en vigueur.

Les questions fondamentales sans réponse aujourd'hui :
- Quel modèle de LLM est le mieux aligné sur une RFE donnée ?
- Quelle approche technique (simple prompt, RAG, MCP, skills, long context, fine-tuning, etc.) produit les réponses les plus fiables ?
- Comment une société savante peut-elle auditer un produit IA qu'une startup lui propose ?

### Qui est concerné

**Utilisateurs primaires :**
- Chercheurs en informatique médicale : besoin de comparer rigoureusement les approches IA
- Sociétés savantes (SFAR, SRLF, SPILF, ESC, ESICM, etc.) : besoin d'auditer les produits IA proposés par les startups
- Startups santé : besoin de prouver l'alignement de leur produit aux recommandations

**Utilisateurs secondaires :**
- Institutions (HAS, HDH) : besoin de référentiels d'évaluation pour les dispositifs à base d'IA
- Communauté académique : besoin de datasets et benchmarks reproductibles

### Situation actuelle

**Comment le problème est géré aujourd'hui :**
- Des études ponctuelles testent des LLMs sur des guidelines (ESC, AAOS, ESMO), mais aucune ne produit un framework réutilisable
- AMEGA (le concurrent le plus proche) évalue sur 13 spécialités avec un scoring LLM-as-judge, mais sans notion d'approche, sans métriques opérationnelles, et sans ciblage de société savante précise
- Aucun outil existant n'est en français

**Points de douleur :**
- Pas de dataset de questions validé et versionné en français pour les RFEs
- Pas de moyen de comparer objectivement RAG vs long context vs MCP vs fine-tuning vs skills
- Les sociétés savantes n'ont aucun outil pour auditer les produits IA qu'on leur propose
- Le scoring LLM-as-judge (utilisé par AMEGA, DeepEval) est non déterministe et peu reproductible

### Impact et urgence

**Impact si non résolu :**
- Les sociétés savantes restent aveugles face aux produits IA proposés par les startups
- Les praticiens utilisent des outils IA sans garantie d'alignement aux recommandations
- La recherche francophone reste absente du paysage des benchmarks médicaux LLM

**Pourquoi maintenant :**
- L'EU AI Act exige des tests pour les systèmes IA à haut risque (art. 10/40) mais ne fournit pas de benchmark
- Le marché des LLMs médicaux explose, les sociétés savantes sont sollicitées par des startups
- Le groupe numérique de la SFAR, dont Thomas fait partie, reçoit des startups qui proposent d'auditer leurs outils IA et cherche un moyen objectif, fiable et reproductible de le faire
- Le projet PARTAGES (HDH, France 2030) vient de publier le corpus PARHAF (mars 2026) : 6 000+ comptes rendus médicaux fictifs en français, en open data (CC BY 4.0). Signe que l'écosystème français se structure pour l'IA médicale, et que les datasets de référence en français deviennent un sujet
- Le congrès SFAR 2026 (16-18 septembre, Paris Porte Maillot) est une opportunité de communication orale/poster (date limite de soumission 21/04)
- npj Digital Medicine a un call for papers ouvert : "Evaluating the Real-World Clinical Performance of AI" (deadline 3 juin 2026), potentiellement aligné avec notre sujet
- L'AMI BOAS (deadline 11 mai 2026) est une opportunité de financement pour ce framework
- Les RFEs SFAR 2024 sur l'ABP sont un cas d'usage idéal pour un premier POC (périmètre maîtrisé, 47 interventions)

---

## 3. Utilisateurs cibles

### Persona 1 : Thomas (chercheur / dev solo)

- **Rôle :** Chercheur postdoc, data scientist
- **Objectifs :** Comparer les approches IA pour la v2 de l'app SFAR ABP ; publier les résultats
- **Points de douleur :** Pas d'outil existant adapté, doit tout construire from scratch
- **Niveau technique :** Expert (Python, LLMs, architecture logicielle)
- **Usage :** Développe, lance les benchmarks, analyse les résultats, rédige les publications

### Persona 2 : Le médecin expert (société savante)

- **Rôle :** Membre d'une commission de société savante (ex. SFAR)
- **Objectifs :** Comprendre si un produit IA est fiable par rapport aux RFEs ; pouvoir dire "ce LLM se trompe sur 30% des recommandations"
- **Points de douleur :** Ne sait pas comment évaluer un LLM, n'a pas les outils techniques
- **Niveau technique :** Non technique
- **Usage :** Consulte les résultats du benchmark, valide les questions du dataset

### Besoins utilisateurs

**Must have :**
- Dataset de questions validé par des experts, versionné, en français
- Scoring déterministe et reproductible (pas de LLM-as-judge)
- Comparaison multi-modèles (Mistral, Claude, GPT, etc.)
- Comparaison multi-approches (RAG, long context, MCP, fine-tuning)
- Métriques opérationnelles : précision, latence, coût, empreinte carbone

**Should have :**
- Architecture extensible à d'autres RFEs / sociétés savantes
- Export des résultats exploitables (CSV, JSON, rapport)

**Nice to have :**
- Interface web -- ou autre -- pour visualiser les résultats (pour les non-techniques)
- Scoring sémantique optionnel (LLM-as-judge en complément)

---

## 4. Solution proposée

### Vue d'ensemble

Un framework Python en architecture port/adaptateur qui :
1. Charge un dataset de questions standardisé (versionné, en français)
2. Interroge N modèles via M approches
3. Score les réponses de manière déterministe
4. Collecte les métriques opérationnelles
5. Produit un rapport comparatif

### Capacités clés

1. **Dataset de benchmark standardisé**
   - Description : 25+ questions avec réponses attendues, issues des RFEs SFAR 2024 ABP
   - Valeur : premier dataset de test en français pour l'évaluation de LLMs sur des recommandations médicales

2. **Moteur de benchmark multi-modèles**
   - Description : interroge un agent, cest-à-dire la combinaison d'un modèle (Mistral, Claude, GPT, etc.) et d'une approche (RAG, MCP, skill, long context, etc.) 
   - Valeur : comparaison objective sur les mêmes questions, dans les mêmes conditions

3. **Scoring déterministe**
   - Description : exact match, fuzzy match, scoring QCM, scoring multi-molécules
   - Valeur : reproductibilité totale, pas de variabilité liée à un LLM-juge

4. **Métriques opérationnelles**
   - Description : précision, latence, tokens, coût, empreinte carbone
   - Valeur : vision complète incluant non seulement la précision, mais aussi la performance, sans oublier les aspects économiques et écologiques

5. **Architecture extensible (port/adaptateur)**
   - Description : toute startup peut implémenter son adaptateur pour être évaluée
   - Valeur : framework ouvert, pas enfermé dans un écosystème

### Ce qui différencie ce projet

Aucun framework existant ne combine :
- Ciblage d'une société savante précise avec des RFEs datées et versionnées
- Comparaison multi-approches (RAG vs long context vs MCP vs fine-tuning vs simple prompt vs ...)
- Métriques opérationnelles (coût, latence, empreinte carbone)
- Scoring déterministe (pas de LLM-as-judge)
- Architecture extensible en open source
- En français

**Proposition de valeur unique :**
Permettre aux sociétés savantes d'auditer l'alignement des produits IA à leurs recommandations, avec un outil scientifique, reproductible et open source.

### MVP (solution minimale viable)

**Fonctionnalités core :**
- Dataset ABP SFAR 25+ questions (source : benchmark.md/json)
- Benchmark multi-modèles via approche "simple prompt"
- Scoring déterministe (exact match + fuzzy)
- Rapport JSON + CSV avec métriques de base (précision, latence, coût)

**Différé :**
- Approches RAG, MCP, long context, skill
- Métriques de performance, économiques/écologiques
- Interface de visualisation
- Extension à d'autres RFEs

---

## 5. Métriques de succès

### Métriques primaires

**Précision des modèles**
- Baseline : inconnu (pas de benchmark existant)
- Cible : avoir des résultats interprétables sur 3+ modèles
- Timeline : POC terminé avant la fin du mois (21 avril 2026) pour soumission au congrès SFAR, puis AMI BOAS (mai 2026)
- Mesure : % de réponses correctes par modèle et par approche

**Publications acceptées**
- Baseline : 0
- Cible : 1+ publication acceptée (orale ou écrite)
- Timeline : soumission avant la fin du mois (21 avril 2026) pour soumission abstract au congrès SFAR, puis AMI BOAS (fin mai 2026), et enfin call for papers npj medecine (3 juin 2026)
- Mesure : acceptation par un comité de lecture

**Adoption du framework**
- Baseline : 0
- Cible : 1+ société savante intéressée par l'extension à d'autres RFEs
- Timeline : 12 mois
- Mesure : contact formel ou collaboration

### Métriques secondaires

- Nombre de questions dans le dataset (objectif : 25+ pour ABP, extensible)
- Nombre de modèles testés (objectif : 3+)
- Qualité du dataset : validation par au moins 1 expert clinicien

### Critères de succès

**Must achieve :**
- Résultats de benchmark exploitables et présentables sur l'ABP SFAR
- Les médecins comprennent et sont convaincus de l'intérêt de benchmarker les LLMs en santé

**Should achieve :**
- Au moins 1 publication acceptée
- Intégration dans le dossier AMI BOAS

---

## 6. Marché et concurrence

### Contexte

Le marché de l'IA en santé est en pleine croissance, avec des centaines de startups proposant des outils à base de LLM. Les sociétés savantes sont sollicitées mais n'ont pas les outils pour évaluer ces produits. L'EU AI Act va imposer des exigences de test, sans fournir de benchmark.

### Paysage concurrentiel

**AMEGA (concurrent direct le plus sérieux)**
- Forces : framework open source, 163 questions, 13 spécialités, peer-reviewed (npj Digital Medicine)
- Faiblesses : généraliste, scoring LLM-as-judge, pas de métriques opérationnelles, pas d'approches multiples, anglophone
- Position : référence académique internationale

**HealthBench (OpenAI)**
- Forces : 5 000 conversations, 262 médecins, 26 spécialités
- Faiblesses : généraliste, construit par OpenAI pour évaluer leurs modèles, anglophone
- Position : benchmark propriétaire orienté OpenAI

**Études ponctuelles (ESC, AAOS, ESMO, etc.)**
- Forces : validées par des cliniciens, publiées dans des revues peer-reviewed
- Faiblesses : non réutilisables, non extensibles, anglophones
- Position : littérature de référence mais pas des outils

### Avantages concurrentiels

- Premier framework en français ciblant des RFEs précises
- Architecture extensible (port/adaptateur) pour d'autres sociétés savantes
- Scoring déterministe vs LLM-as-judge
- Métriques opérationnelles (coût, latence, carbone)
- Double valeur : benchmark publiable + framework réutilisable

---

## 7. Modèle économique

Pas de modèle de revenus direct. Le projet est un outil de recherche open source.

**Valorisation :**
- Publications scientifiques (crédibilité académique)
- Intégration dans l'AMI BOAS (financement potentiel)
- Positionnement comme référence pour l'audit des LLMs médicaux en France
- Collaborations avec les startups qui viennent voir la SFAR : elles bénéficient d'une évaluation indépendante et crédible de leur produit, le projet gagne en visibilité, en données de terrain, et potentiellement en co-financement ou co-publication

---

## 8. Considérations techniques

### Stack technique

- **Python 3.12** avec `uv`
- **LiteLLM** : proxy unifié pour les appels API multi-providers
- **Architecture port/adaptateur** : `ApproachPort` / `LLMPort` / `ScoringPort`
- **Linter/formatter** : `ruff`

### Intégrations requises

- API Mistral (Mistral Large, Small)
- API Anthropic (Claude)
- API OpenAI (GPT-4o, o3-mini)

### Contraintes techniques

- Reproductibilité : température 0, seed fixe quand possible
- Pas de dépendance à un service tiers pour le scoring (déterministe local)
- Coût par run de benchmark maîtrisé (< 1 EUR par exécution complète)

---

## 9. Risques et mitigation

### Risques prioritaires

**Risque 1 : Qualité du dataset**
- Probabilité : moyenne
- Impact : critique (si les questions sont mauvaises, les résultats sont inutiles)
- Mitigation : validation par au moins 1 expert clinicien (Thomas connaît le domaine)
- Owner : Thomas

**Risque 2 : Scoring trop simpliste**
- Probabilité : haute
- Impact : moyen (exact match peut rater des réponses correctes formulées différemment)
- Mitigation : scoring multi-niveaux (exact, fuzzy, mots-clés), prompt engineering pour forcer un format de réponse
- Owner : Thomas

**Risque 3 : Pas de publication acceptée**
- Probabilité : haute
- Impact : moyen (le framework existe quand même, mais la visibilité est réduite)
- Mitigation : cibler des venues variées (congrès + revue), angle original (français, multi-approches)
- Owner : Thomas

### Hypothèses critiques

- Les RFEs SFAR sont suffisamment structurées pour en extraire un dataset de questions non ambiguës
- Le scoring déterministe est suffisant pour produire des résultats interprétables (sinon ajouter LLM-as-judge en complément)
- L'architecture port/adaptateur est réellement extensible à d'autres RFEs sans refonte majeure

---

## 10. Ressources

### Equipe

**Phase POC (actuel) :**
- Thomas Boulier (chercheur/dev solo ; ingénieur polytechnicien + PhD mathématiques appliquées & médecin anesthésiste-réanimateur) : 100% sur la partie technique + publications

**Phase scale-up (après POC) :**
- Membres du groupe numérique SFAR : portage institutionnel, extension à d'autres RFEs
- Experts cliniciens (MARs, infectiologues) : validation et enrichissement du dataset, co-publications
- Startups partenaires : apportent leurs approches à évaluer via le framework
- Autres sociétés savantes, reste de la communauté médicale : extension du dataset à d'autres spécialités (sur le modèle PARTAGES/PARHAF)

### Dépendances

**Internes :**
- App SFAR ABP existante (https://github.com/tomboulier/recos-antibioprophylaxie-SFAR) : source des données RFE
- Dataset benchmark.md/json déjà existant (25 questions)

**Externes :**
- APIs LLM (Anthropic, OpenAI, Mistral) : disponibilité et coûts
- Validation clinique : relecture par un expert médical

---

## 11. Prochaines étapes

1. Relire et enrichir le dataset (`benchmark.json`, généré par IA) : valider les questions existantes + ajouter des questions couvrant d'autres chirurgies que l'ortho/traumato
2. Revoir le code existant (développé par Kiro) : valider ou non l'architecture et le code, décider si on l'améliore ou si on repart from scratch
3. Finaliser le moteur de benchmark (AC3 du S-019 : multi-modèles + scoring)
4. Lancer les premiers runs et collecter les résultats
5. Rédiger le findings report avec recommandations
6. Soumettre une première publication (benchmark + résultats)
7. Intégrer dans le dossier AMI BOAS si pertinent

### Phase suivante recommandée

Passer au **PRD** avec le Product Manager pour formaliser les exigences fonctionnelles et non-fonctionnelles du framework.

**Handoff vers :** Product Manager (`bmad-product-manager`)

---

## Annexe

### Sources de recherche

- Comparaison des frameworks : `docs/llm-eval-frameworks-comparison.md`
- RFEs SFAR ABP 2024 : https://sfar.org/wp-content/uploads/2024/02/RFE-antibioprophylaxie-2023_V1.3_pour-mise-sur-site-janvier-2024.pdf
- AMEGA : https://github.com/DATEXIS/AMEGA-benchmark/
- HealthBench : https://openai.com/index/healthbench/
- Swedish Medical LLM Benchmark (SMLB) : Frontiers in AI, juin 2025 (angle "benchmark national + langue non anglaise", comme nous pour le français)

---

**Statut du document :** Draft
**Derniere mise a jour :** 2026-03-27
