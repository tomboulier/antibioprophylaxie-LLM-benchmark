# PRD : medical-llm-benchmark

**Date :** 2026-03-28
**Auteur :** Thomas Boulier (avec assistance IA)
**Statut :** Draft
**Version :** 1.0
**Source :** Product Brief v1.0 (`docs/product-brief.md`)

---

## 1. Objectif du document

Ce PRD formalise les exigences fonctionnelles et non fonctionnelles du framework de benchmark, les organise en epics et user stories, et les priorise avec MoSCoW. Il sert de guide de développement pour Thomas (solo dev) et de référence pour les futures publications.

### Priorisation MoSCoW

- **MUST** : indispensable pour le POC et la publication
- **SHOULD** : important, prévu dans les sprints suivants
- **COULD** : bonus si le temps le permet
- **WONT** : explicitement hors scope pour la V1

---

## 2. Scope

**In scope :**
- Dataset de questions ABP SFAR 2024 (60-80 questions cible)
- Benchmark multi-modèles x multi-approches
- Scoring déterministe multi-critères
- Métriques opérationnelles (précision, latence, coût, carbone)
- Export JSON/CSV + rapport comparatif
- Architecture extensible (ports & adaptateurs)

**Out of scope (V1) :**
- Interface web grand public
- Intégration dans l'app SFAR principale
- Extension à d'autres RFEs (architecture prévue, pas l'implémentation)
- Certification réglementaire

---

## 3. Exigences fonctionnelles

### 3.1 Dataset et questions

**FR-001 : MUST -- Le système doit charger et valider un dataset de questions au format JSON standardisé**

Critères d'acceptation :
1. Le `DatasetLoader` charge un fichier JSON contenant des questions avec les champs obligatoires : `id`, `question`, `expected_answer`, `question_type` (open / mcq)
2. Le chargement échoue avec une erreur explicite si un champ obligatoire est absent ou mal typé
3. Le dataset est versionné (champ `version` au niveau racine, versioning sémantique)
4. Le loader accepte les métadonnées optionnelles par question : `difficulty`, `clinical_impact`, `category`, `source_rfe`, `explanation` (justification de la réponse attendue, pour analyse qualitative)

**FR-002 : MUST -- Chaque question du dataset doit comporter des critères de scoring structurés**

Critères d'acceptation :
1. Les questions ouvertes contiennent un champ `scoring_criteria` avec au moins un critère (ex. `molecule`, `dose`, `voie`, `timing`)
2. Chaque critère définit les valeurs attendues (`expected`), les synonymes acceptés (`accepted_synonyms`), et un poids (`weight`)
3. Les questions QCM contiennent les choix (`choices`) et la ou les réponses correctes (`correct_answers`)
4. Le schéma JSON du dataset est documenté et validable par un JSON Schema

**FR-003 : SHOULD -- Le dataset doit couvrir au minimum 60 questions pour la V1 publication**

Critères d'acceptation :
1. Le dataset contient au moins 60 questions couvrant les différentes spécialités des RFE SFAR 2024 ABP
2. La répartition comprend des questions ouvertes et des QCM
3. Chaque question est annotée avec un niveau de difficulté (facile, moyen, difficile) et un impact clinique (faible, modéré, critique)
4. Le dataset est compatible avec le format HuggingFace Datasets pour publication et citabilité

**FR-004 : SHOULD -- Le dataset doit supporter des tables de synonymes pour les molécules et les termes médicaux**

Critères d'acceptation :
1. Une table de synonymes centralise les équivalences (DCI, noms commerciaux, variantes orthographiques) pour chaque molécule
2. Le scoring utilise automatiquement ces tables lors de la comparaison réponse / attendu
3. La table est extensible sans modification du code (fichier de configuration séparé)

### 3.2 Moteur de benchmark (orchestration)

**FR-005 : MUST -- Le moteur doit exécuter un benchmark sur toute combinaison (modèle x approche x dataset)**

Critères d'acceptation :
1. Le `BenchmarkEngine` accepte une liste de modèles, une liste d'approches, et un dataset en entrée
2. Chaque combinaison (modèle, approche) est exécutée sur chaque question du dataset
3. Les résultats sont structurés par combinaison avec les réponses brutes, les scores et les métriques
4. L'exécution est séquentielle par défaut pour garantir la reproductibilité

**FR-006 : MUST -- Le moteur doit garantir la reproductibilité des résultats**

Critères d'acceptation :
1. Tous les appels LLM utilisent temperature=0 et un seed fixe quand le provider le supporte
2. Les paramètres d'exécution complets sont enregistrés dans les résultats (modèle, version, date, paramètres)
3. Un même run sur un même dataset produit des scores identiques (hors variabilité résiduelle du provider)
4. Le hash du dataset utilisé est enregistré dans les résultats

**FR-007 : MUST -- Le prompt doit forcer le LLM à répondre dans un format structuré pour permettre un scoring déterministe**

Critères d'acceptation :
1. Le prompt demande explicitement au LLM de répondre au format structuré (JSON ou champs séparés : molécule, dose, voie, réinjection)
2. Le format de réponse attendu correspond aux champs des `scoring_criteria` du dataset
3. La réponse brute du LLM est conservée en plus de la réponse parsée, pour audit
4. Si le LLM ne respecte pas le format demandé, la réponse est marquée comme non parsable (et non comme incorrecte)

**FR-008 : MUST -- Le moteur doit gérer les erreurs et timeouts sans interrompre le benchmark**

Critères d'acceptation :
1. Si un appel LLM échoue (timeout, erreur API, rate limit), l'erreur est enregistrée et le benchmark continue avec la question suivante
2. Un mécanisme de retry configurable (nombre de tentatives, délai) est disponible
3. Le rapport final distingue les réponses évaluées des erreurs
4. Le coût des appels échoués est tout de même comptabilisé

### 3.3 Scoring

**FR-009 : MUST -- Le système doit scorer les réponses QCM par correspondance exacte**

Critères d'acceptation :
1. Pour une question QCM, la réponse est correcte si et seulement si elle correspond exactement à la ou aux lettres attendues
2. Le scoring est insensible à la casse et aux espaces superflus
3. Pour les QCM multi-réponses, toutes les réponses attendues doivent être présentes et aucune réponse incorrecte ne doit figurer
4. Le score est binaire : 1 (correct) ou 0 (incorrect)

**FR-010 : MUST -- Le système doit scorer les réponses ouvertes par extraction de champs structurés et comparaison multi-critères**

Critères d'acceptation :
1. Le scorer extrait les champs (molécule, dose, voie, timing) de la réponse du LLM
2. Chaque champ est comparé aux valeurs attendues en tenant compte des synonymes
3. Le score final est la somme pondérée des critères satisfaits, normalisée entre 0 et 1
4. Le détail par critère (satisfait ou non) est disponible dans les résultats
5. Le scorer est entièrement déterministe (pas de LLM dans la boucle de scoring)

**FR-011 : SHOULD -- Le scoring doit supporter des critères de sécurité avec pénalités**

Critères d'acceptation :
1. Un critère peut porter un poids négatif (pénalité) pour sanctionner une réponse dangereuse (ex. antibiotique contre-indiqué chez un patient allergique)
2. Les pénalités de sécurité sont identifiées séparément dans le rapport
3. Le score final peut être négatif si les pénalités dépassent les points positifs
4. L'impact clinique des critères de sécurité est reporté dans les métriques agrégées

**FR-012 : COULD -- Le système pourrait proposer un scoring sémantique optionnel (LLM-as-judge) en complément**

Critères d'acceptation :
1. Un scorer optionnel utilise un LLM pour évaluer les critères résistant au parsing déterministe
2. Ce scorer est désactivable et désactivé par défaut
3. Les scores sémantiques sont reportés séparément des scores déterministes
4. Le scorer sémantique utilise temperature=0 et triple évaluation pour réduire la variance

### 3.4 Métriques et reporting

**FR-013 : MUST -- Le système doit collecter et reporter les métriques opérationnelles pour chaque run**

Critères d'acceptation :
1. Les métriques suivantes sont collectées par question et par combinaison (modèle, approche) : précision (score), latence (secondes), nombre de tokens (input + output), coût estimé (EUR)
2. Les métriques sont agrégées au niveau du run : précision moyenne, latence médiane, coût total
3. Les métriques brutes et agrégées sont exportables
4. La latence mesure le temps réel d'appel API (hors traitement local)

**FR-014 : SHOULD -- Le système doit estimer l'empreinte carbone de chaque run**

Critères d'acceptation :
1. L'empreinte carbone est estimée à partir du nombre de tokens et du provider (facteur d'émission par token ou par kWh)
2. Les facteurs d'émission sont configurables par provider et par région
3. L'empreinte est reportée en gCO2eq par run et par question
4. La méthodologie d'estimation est documentée dans le rapport

**FR-015 : MUST -- Le système doit exporter les résultats en JSON et CSV**

Critères d'acceptation :
1. L'export JSON contient toutes les données brutes (questions, réponses, scores, métriques, paramètres)
2. L'export CSV contient un résumé tabulaire exploitable dans un tableur (une ligne par combinaison modèle x approche x question)
3. Les fichiers de sortie sont nommés avec un horodatage pour éviter les écrasements
4. Le format JSON est documenté et stable (versionné)

**FR-016 : SHOULD -- Le système doit produire un rapport comparatif lisible**

Critères d'acceptation :
1. Le rapport présente un classement des combinaisons (modèle x approche) par précision
2. Le rapport inclut un tableau comparatif avec précision, latence, coût et empreinte carbone
3. Le rapport identifie les points forts et faiblesses de chaque approche (ex. catégories de questions où l'approche échoue)
4. Le rapport est généré au format Markdown ou HTML

### 3.5 Approches (RAG, MCP, long context, etc.)

**FR-017 : MUST -- Le système doit supporter au minimum deux approches : simple prompt et long context**

Critères d'acceptation :
1. L'approche "simple prompt" envoie la question seule au LLM sans contexte supplémentaire
2. L'approche "long context" injecte le texte intégral de la RFE dans la fenêtre de contexte du LLM
3. Chaque approche implémente le port `ApproachPort` et est enregistrée dans le registre
4. Les deux approches sont testables sur tous les modèles configurés

**FR-018 : SHOULD -- Le système doit supporter les approches RAG (PDF et données structurées)**

Critères d'acceptation :
1. L'approche RAG PDF effectue un retrieval sur le document PDF de la RFE, puis transmet les passages pertinents au LLM
2. L'approche RAG structurée effectue un retrieval sur une base de données structurée (export Excel/CSV/JSON de la RFE)
3. Chaque approche RAG enregistre les passages récupérés (chunks) dans les résultats pour traçabilité
4. Les paramètres de retrieval (top-k, seuil de similarité) sont configurables

**FR-019 : SHOULD -- Le système doit supporter l'approche MCP (Model Context Protocol)**

Critères d'acceptation :
1. L'approche MCP met à disposition du LLM un ou plusieurs outils (tools) pour interroger les données de la RFE
2. Les appels aux outils sont enregistrés dans les résultats (nombre d'appels, outils utilisés)
3. L'approche implémente le port `ApproachPort` et est interchangeable avec les autres approches
4. Le comportement est reproductible avec les mêmes paramètres

### 3.6 Extensibilité

**FR-020 : SHOULD -- Le framework doit être extensible à d'autres RFEs et sociétés savantes sans modification du code métier**

Critères d'acceptation :
1. Un nouveau dataset (autre RFE, autre société savante) peut être chargé sans modifier le `BenchmarkEngine` ni le `ScorerRegistry`
2. Le format de dataset est générique (pas de champ spécifique à l'antibioprophylaxie dans le schéma obligatoire)
3. Les tables de synonymes sont paramétrables par dataset
4. La documentation décrit la procédure pour ajouter un nouveau dataset

**FR-021 : SHOULD -- Le framework doit permettre à un tiers d'ajouter une nouvelle approche via un adaptateur**

Critères d'acceptation :
1. L'ajout d'une approche se fait en implémentant le port `ApproachPort` et en enregistrant l'adaptateur dans le registre
2. Aucune modification du moteur de benchmark n'est nécessaire
3. Un tiers (ex. une startup) peut fournir son adaptateur sous forme de module Python indépendant
4. La documentation décrit la procédure pour ajouter une nouvelle approche, avec un exemple

### 3.7 Visualisation

**FR-022 : COULD -- Le système pourrait proposer une interface de visualisation des résultats pour les utilisateurs non techniques**

Critères d'acceptation :
1. L'interface affiche le tableau comparatif des combinaisons (modèle x approche) avec les métriques clés
2. L'interface permet de filtrer par modèle, par approche, et par catégorie de question
3. L'interface est accessible sans installation technique (notebook Marimo, page HTML statique, ou équivalent)
4. Les données sont chargées à partir des exports JSON produits par le benchmark

**FR-023 : COULD -- Le dataset pourrait être exposé comme plateforme de QCMs à visée de formation continue pour les anesthésistes-réanimateurs**

Critères d'acceptation :
1. Les questions du dataset sont présentées sous forme de QCMs interactifs (question, choix ou réponse courte, puis correction)
2. Le champ `explanation` est affiché après chaque réponse pour expliquer la réponse attendue et son fondement dans la RFE
3. Les questions sont filtrables par catégorie chirurgicale et par niveau de difficulté
4. La plateforme est accessible en ligne sans installation (app web légère, notebook Marimo, ou équivalent)

> **Note :** Cette exigence est une perspective de valorisation du dataset au-delà du benchmark. Le même jeu de questions validé par des experts sert à la fois à évaluer les LLMs et à former les praticiens. C'est un argument fort pour convaincre les sociétés savantes de contribuer au dataset.

---

## 4. Exigences non fonctionnelles

### 4.1 Reproductibilité

**NFR-001 : MUST -- Les résultats du benchmark doivent être reproductibles à l'identique entre deux exécutions successives.**

- Chaque appel LLM utilise `temperature=0` et un `seed` fixe lorsque l'API le permet.
- Le scoring est entièrement déterministe (pas de LLM-as-judge non contrôlé, pas de random).
- Deux runs consécutifs sur le même commit, avec les mêmes clés API, produisent des fichiers de résultats identiques (hash SHA-256 identique sur les colonnes de scoring).

**NFR-002 : MUST -- Chaque run doit être traçable et auditable.**

- Les métadonnées de chaque run sont enregistrées : commit git, timestamp, versions des modèles appelés, paramètres d'inférence.
- Les résultats bruts (réponses complètes des LLM) sont conservés dans `research/results/` au format JSON.
- Un identifiant unique de run (`run_id`) permet de relier métadonnées, résultats bruts et scores.

### 4.2 Performance

**NFR-003 : MUST -- Le coût total d'un run complet (toutes approches, tous modèles) doit rester inférieur à 1 EUR.**

- Le nombre de tokens consommés (input + output) est mesuré et enregistré pour chaque requête.
- Le coût estimé par modèle est calculé à partir des tarifs publics et affiché en fin de run.
- Un mécanisme de dry-run permet de simuler le coût avant exécution réelle.

**NFR-004 : SHOULD -- La latence d'un run complet ne doit pas dépasser 10 minutes.**

- Le temps d'exécution par question et par approche est mesuré et enregistré.
- Les appels API sont parallélisés par approche lorsque c'est possible (rate limits respectés).

### 4.3 Qualité du code

**NFR-005 : MUST -- Le code doit respecter les standards de qualité définis par le projet.**

- `uv run ruff check .` ne retourne aucune erreur ni warning.
- `uv run ruff format --check .` ne retourne aucune différence.
- La couverture de tests est >= 80 % sur la logique métier (scoring, parsing, orchestration), mesurée par `pytest-cov`.

**NFR-006 : MUST -- Les commits suivent la convention Conventional Commits en français.**

- Format : `type(scope): description en français` (types : feat, fix, docs, chore, test, refactor).
- Chaque PR passe un lint de message de commit (CI ou pre-commit hook).

### 4.4 Extensibilité

**NFR-007 : SHOULD -- Ajouter un nouveau modèle LLM ne doit nécessiter qu'une modification de configuration.**

- L'ajout d'un modèle se fait uniquement via un fichier de config (YAML ou dict Python), sans modifier le code d'orchestration.
- L'ajout d'une nouvelle approche se fait en créant une classe implémentant `ApproachPort` et en l'enregistrant dans le registre, sans toucher au code existant.
- Un test d'intégration vérifie que le registre charge correctement toutes les approches déclarées.

### 4.5 Portabilité

**NFR-008 : MUST -- Le projet doit fonctionner sur Linux et macOS sans dépendance système exotique.**

- Les seuls prérequis système sont Python 3.12+ et `uv`.
- `uv sync --extra dev` installe toutes les dépendances nécessaires sans étape manuelle supplémentaire.
- Aucune dépendance ne requiert de bibliothèque C non standard ou de binaire pré-compilé spécifique à une plateforme.

### 4.6 Documentation

**NFR-010 : SHOULD -- Les fonctions publiques doivent être documentées au format numpydoc.**

- Chaque fonction et classe publique possède une docstring avec sections `Parameters`, `Returns` et `Examples` si pertinent.
- Le README du projet contient les instructions d'installation, d'exécution et de contribution, vérifiées à chaque release.

### 4.7 Données

**NFR-011 : MUST -- Le dataset de questions doit être versionné et compatible avec une publication ouverte.**

- Le fichier `research/benchmark.md` est la source de vérité ; `benchmark.json` est généré et versionné.
- Le format JSON est compatible HuggingFace Datasets (chargeable via `datasets.load_dataset`).
- Chaque modification du dataset incrémente un numéro de version sémantique dans les métadonnées.

### 4.8 Sécurité

**NFR-012 : MUST -- Aucune clé API ou secret ne doit apparaître dans le code source ou l'historique git.**

- Les clés API sont lues exclusivement depuis des variables d'environnement ou un fichier `.env` (listé dans `.gitignore`).
- Un fichier `.env.example` documente les variables attendues sans valeur réelle.
- Un hook pre-commit (ou règle ruff) détecte les patterns de clés API avant tout commit.

### 4.9 Écologie

**NFR-013 : SHOULD -- L'empreinte carbone de chaque run doit être estimée et enregistrée.**

- Le nombre de tokens consommés et le fournisseur utilisé sont enregistrés pour chaque requête.
- Une estimation des émissions CO2 (en gCO2eq) est calculée par run à partir des données publiques d'intensité carbone des datacenters.
- L'empreinte carbone apparaît dans le rapport de résultats aux côtés du coût financier.

---

## 5. Epics et User Stories

### Epic 1 : POC Demo (Sprint 1, deadline 2 avril)

**Valeur métier** : Disposer d'un prototype fonctionnel à montrer aux collègues du groupe numérique SFAR le 2 avril, prouvant la faisabilité du benchmark multi-modèles.

**Exigences couvertes** : FR-001, FR-005, FR-006, FR-007, FR-008, FR-009, FR-013, FR-015, FR-017, NFR-001, NFR-003, NFR-005, NFR-008, NFR-012

**Stories** :

**S1.1** -- En tant que Thomas, je veux lancer un benchmark sur au moins 2 modèles (Claude, GPT-4o) avec une seule commande CLI afin de démontrer le fonctionnement du framework en live.

Critères d'acceptation :
- `uv run python scripts/run_benchmark.py -m claude-sonnet -m gpt-4o` exécute le benchmark de bout en bout sans erreur
- Les résultats sont écrits dans `research/results/` au format JSON horodaté
- Le temps d'exécution total est inférieur à 5 minutes pour 23 questions x 2 modèles

**S1.2** -- En tant que Thomas, je veux un scoring binaire automatique (correct/incorrect) comparant la réponse du LLM à la réponse attendue afin d'obtenir un pourcentage de précision par modèle.

Critères d'acceptation :
- Chaque réponse est scorée automatiquement sans intervention manuelle
- Le score global (% correct) est affiché en fin d'exécution dans le terminal
- Les cas d'échec sont identifiables dans le JSON de résultats (champ `is_correct`)

**S1.3** -- En tant que Thomas, je veux un tableau récapitulatif lisible (terminal ou CSV) comparant les scores des modèles testés afin de préparer un support visuel pour la démo SFAR.

Critères d'acceptation :
- Un fichier CSV est généré dans `research/results/` avec colonnes : modèle, score, nombre de questions
- Le tableau est aussi affiché dans le terminal en fin de run
- Le format est directement importable dans un tableur ou un notebook

**S1.4** -- En tant que Thomas, je veux que le dataset de 23 questions existant (`research/benchmark.md`) soit compilable en JSON valide afin d'alimenter le pipeline de benchmark.

Critères d'acceptation :
- `uv run python scripts/benchmark_md_to_json.py` produit un `benchmark.json` valide
- Le JSON contient au moins 23 entrées avec les champs `question`, `expected_answer`, `category`
- Un test unitaire vérifie la structure du JSON généré

---

### Epic 2 : Dataset enrichi

**Valeur métier** : Un dataset de 23 questions centré sur l'orthopédie est insuffisant pour une publication. Élargir à 60-80 questions couvrant toutes les sections du RFE renforce la crédibilité scientifique.

**Exigences couvertes** : FR-001, FR-002, FR-003, FR-004, NFR-011

**Stories** :

**S2.1** -- En tant que Thomas, je veux ajouter des questions couvrant toutes les sections du RFE SFAR 2024 (digestif, urologie, gynécologie, cardiaque, etc.) afin que le benchmark ne soit pas biaisé vers une seule spécialité.

Critères d'acceptation :
- Au moins 8 sections chirurgicales du RFE sont couvertes par au moins 3 questions chacune
- Le champ `category` du JSON reflète la section RFE correspondante
- Le total atteint au moins 60 questions compilables sans erreur

**S2.2** -- En tant que Thomas, je veux enrichir chaque question avec des métadonnées (difficulté, impact clinique, type de question) afin de stratifier les résultats dans l'analyse.

Critères d'acceptation :
- Chaque entrée du JSON contient les champs `difficulty` (easy/medium/hard) et `clinical_impact` (low/medium/high)
- Le parser `benchmark_md_to_json.py` extrait ces métadonnées depuis le format Markdown
- Un test vérifie qu'aucune question n'a de métadonnée manquante

**S2.3** -- En tant que Thomas, je veux définir des synonymes acceptables pour les molécules et posologies (ex. "céfazoline" / "céphazoline" / "kéfzol") afin de réduire les faux négatifs lors du scoring.

Critères d'acceptation :
- Un fichier de référence (`research/synonyms.yaml` ou similaire) liste les équivalences acceptées
- Le scoring utilise cette table pour normaliser les réponses avant comparaison
- Au moins 10 molécules du RFE ont leurs synonymes courants définis

**S2.4** -- En tant que Thomas, je veux inclure des questions pièges (patient allergique, intervention sans antibioprophylaxie recommandée) afin de tester la capacité des LLM à ne pas sur-prescrire.

Critères d'acceptation :
- Au moins 5 questions testent un cas où la réponse attendue est "pas d'antibioprophylaxie"
- Au moins 3 questions testent une allergie imposant une alternative thérapeutique
- Ces questions sont identifiées par un tag `type: negative` ou `type: allergy`

---

### Epic 3 : Scoring multi-critères

**Valeur métier** : Un scoring binaire perd trop d'information. Un scoring décomposé (molécule, dose, voie, timing) permet d'identifier précisément où chaque approche échoue et de publier une analyse granulaire.

**Exigences couvertes** : FR-002, FR-010, FR-011, FR-012

**Stories** :

**S3.1** -- En tant que Thomas, je veux que chaque réponse soit scorée sur 4 dimensions indépendantes (molécule, dose, voie d'administration, timing) afin de produire un profil d'erreur par modèle.

Critères d'acceptation :
- Le JSON de résultats contient un sous-objet `score_detail` avec les 4 dimensions
- Chaque dimension est notée 0 ou 1 (correct/incorrect)
- Le score global est la moyenne pondérée des 4 dimensions

**S3.2** -- En tant que Thomas, je veux définir des pondérations configurables par dimension (ex. molécule x2, dose x1.5, voie x1, timing x1) afin de refléter l'importance clinique relative.

Critères d'acceptation :
- Les poids sont définis dans un fichier de configuration (`config/scoring.yaml` ou similaire)
- Modifier les poids ne nécessite aucun changement de code
- Un test vérifie que le score pondéré est correctement calculé sur un exemple connu

**S3.3** -- En tant que Thomas, je veux un système de crédit partiel (ex. bonne molécule mais mauvaise dose = 0.5) afin de différencier une réponse partiellement correcte d'une réponse totalement fausse.

Critères d'acceptation :
- Le score total par question est un float entre 0.0 et 1.0
- Les résultats CSV distinguent les cas "totalement correct", "partiellement correct", "incorrect"
- La distribution des scores partiels est visible dans le récapitulatif

**S3.4** -- En tant que Thomas, je veux détecter automatiquement les erreurs de sécurité critiques (mauvaise molécule chez un allergique, dose toxique) afin de les signaler séparément dans les résultats.

Critères d'acceptation :
- Un flag `safety_error` est ajouté aux résultats quand une erreur critique est détectée
- Les critères de sécurité sont définis dans le fichier de configuration du scoring
- Le récapitulatif affiche le nombre d'erreurs de sécurité par modèle

---

### Epic 4 : Approches avancées

**Valeur métier** : Le coeur du benchmark est la comparaison de 5 approches d'IA. Chaque approche doit être testée dans des conditions reproductibles pour alimenter la publication scientifique.

**Exigences couvertes** : FR-017, FR-018, FR-019, FR-021, NFR-007

**Stories** :

**S4.1** -- En tant que Thomas, je veux une interface `ApproachPort` simple (protocole Python) afin que chaque approche implémente la même signature et soit interchangeable dans le pipeline.

Critères d'acceptation :
- Le protocole définit une méthode `query(question: str) -> str` (et éventuellement des métadonnées)
- Au moins l'approche "simple prompt" implémente ce protocole
- Un test vérifie qu'un adaptateur respecte le protocole

**S4.2** -- En tant que Thomas, je veux un adaptateur RAG-PDF qui indexe le PDF du RFE et répond via retrieval afin de comparer cette approche au long context.

Critères d'acceptation :
- L'adaptateur indexe `research/rfe-sfar-2024.pdf` au premier run
- Les réponses sont générées à partir des chunks récupérés
- Le benchmark peut être lancé avec `--approach rag-pdf`

**S4.3** -- En tant que Thomas, je veux un adaptateur RAG-structuré qui utilise l'export Excel/CSV du RFE afin de tester si la donnée structurée améliore la précision.

Critères d'acceptation :
- L'adaptateur charge les données depuis un fichier structuré (CSV ou Excel)
- Le retrieval exploite les colonnes (chirurgie, molécule, dose, etc.)
- Les résultats sont comparables aux autres approches via le même scoring

**S4.4** -- En tant que Thomas, je veux un adaptateur MCP (Model Context Protocol) exposant le RFE via des tools afin de tester l'approche agentic.

Critères d'acceptation :
- Un serveur MCP minimal expose au moins 2 tools (ex. `get_protocol`, `search_molecule`)
- L'adaptateur se connecte au serveur et utilise les tools pour répondre
- Le benchmark peut être lancé avec `--approach mcp`

**S4.5** -- En tant que Thomas, je veux un adaptateur fine-tuning qui utilise un modèle affiné sur le RFE afin de comparer cette approche aux autres.

Critères d'acceptation :
- Un script de préparation du dataset de fine-tuning est fourni
- L'adaptateur interroge le modèle fine-tuné via l'API du provider
- Le coût du fine-tuning est documenté pour le rapport comparatif

---

### Epic 5 : Métriques opérationnelles

**Valeur métier** : La précision seule ne suffit pas pour recommander une approche en production. La latence, le coût et l'empreinte carbone sont des critères décisionnels pour la SFAR et pour la publication.

**Exigences couvertes** : FR-013, FR-014, FR-015, FR-016, NFR-003, NFR-004, NFR-013

**Stories** :

**S5.1** -- En tant que Thomas, je veux mesurer la latence (temps de réponse) et le nombre de tokens consommés pour chaque requête afin de comparer l'efficience des approches.

Critères d'acceptation :
- Chaque entrée du JSON de résultats contient `latency_ms` et `tokens_used` (input + output)
- Les valeurs sont mesurées côté client (wall clock) et côté API (si disponible)
- Le récapitulatif affiche la latence moyenne et le total de tokens par modèle

**S5.2** -- En tant que Thomas, je veux estimer le coût en euros par requête et par run complet afin d'évaluer la viabilité économique de chaque approche.

Critères d'acceptation :
- Les tarifs par token sont configurables dans un fichier de pricing
- Le coût est calculé automatiquement et ajouté aux résultats
- Le récapitulatif affiche le coût total par approche

**S5.3** -- En tant que Thomas, je veux estimer l'empreinte carbone de chaque run (gCO2eq) afin d'inclure ce critère dans la publication.

Critères d'acceptation :
- L'estimation utilise une méthodologie documentée (ex. coefficients ML CO2 Impact)
- Le résultat est exprimé en gCO2eq par run et par question
- La méthodologie est citée dans le rapport

**S5.4** -- En tant que Thomas, je veux exporter toutes les métriques en CSV et JSON normalisés afin de les exploiter dans des notebooks d'analyse.

Critères d'acceptation :
- Les exports contiennent toutes les colonnes : approche, modèle, question_id, score, latence, tokens, coût, CO2
- Les fichiers sont horodatés et versionnés dans `research/results/`
- Un notebook peut charger le CSV sans transformation préalable

---

### Epic 6 : Publication et diffusion

**Valeur métier** : Le benchmark n'a d'impact que s'il est publié et reproductible. Un dataset ouvert, un rapport automatisé et des visualisations prêtes à l'emploi maximisent la portée scientifique.

**Exigences couvertes** : FR-003, FR-016, FR-022, NFR-010, NFR-011

**Stories** :

**S6.1** -- En tant que Thomas, je veux générer automatiquement un rapport comparatif (Markdown ou HTML) à partir des résultats afin de produire le findings report sans travail manuel.

Critères d'acceptation :
- `uv run python scripts/eval_results.py` génère `docs/findings-report.md`
- Le rapport contient un tableau comparatif, des graphiques descriptifs et une recommandation
- Le rapport est re-générable à chaque nouveau run sans modification du script

**S6.2** -- En tant que Thomas, je veux publier le dataset de questions sur HuggingFace Datasets afin qu'il soit réutilisable par d'autres chercheurs.

Critères d'acceptation :
- Un script de packaging prépare le dataset au format HuggingFace (dataset card incluse)
- Le dataset est versionné et contient les métadonnées (licence, citation, description)
- Le README du dataset décrit la méthodologie de construction

**S6.3** -- En tant que Thomas, je veux obtenir un DOI Zenodo pour le dataset et le code afin de les rendre citables dans les publications.

Critères d'acceptation :
- Le dépôt GitHub est lié à Zenodo via le webhook de release
- Un fichier `.zenodo.json` contient les métadonnées de citation
- Le DOI est référencé dans le README du projet

**S6.4** -- En tant que Thomas, je veux un notebook Marimo interactif pour explorer les résultats visuellement afin de préparer les figures pour les articles et les présentations.

Critères d'acceptation :
- Le notebook charge les résultats CSV et affiche les comparaisons par approche
- Au moins 3 visualisations sont incluses : précision par approche, latence, coût
- Le notebook est exécutable avec `uv run marimo run notebooks/analysis.py`

---

## 6. Matrice de traçabilité

| Epic | FR couvertes | NFR couvertes | Priorité MoSCoW |
|------|-------------|---------------|-----------------|
| Epic 1 : POC Demo | FR-001, 005-009, 013, 015, 017 | NFR-001, 003, 005, 008, 011 | MUST |
| Epic 2 : Dataset enrichi | FR-001-004 | NFR-010 | SHOULD |
| Epic 3 : Scoring multi-critères | FR-002, 007, 010-012 | NFR-001 | SHOULD |
| Epic 4 : Approches avancées | FR-017-019, 021 | NFR-007 | SHOULD |
| Epic 5 : Métriques opérationnelles | FR-013-016 | NFR-003, 004, 012 | SHOULD |
| Epic 6 : Publication et diffusion | FR-003, 016, 022-023 | NFR-009, 010 | COULD |

---

## 7. Hypothèses et dépendances

### Hypothèses

1. Les RFE SFAR 2024 ABP sont suffisamment structurées pour en extraire 60+ questions non ambiguës
2. Le scoring déterministe (exact match + synonymes + multi-critères) est suffisant pour produire des résultats interprétables
3. Les APIs des providers LLM (Anthropic, OpenAI, Mistral) restent stables et accessibles pendant la durée du projet
4. L'architecture port/adaptateur est extensible à d'autres RFEs sans refonte majeure

### Dépendances

| Dépendance | Type | Impact si indisponible |
|-----------|------|----------------------|
| APIs LLM (Anthropic, OpenAI, Mistral) | Externe | Bloquant pour l'exécution des benchmarks |
| RFE SFAR 2024 (PDF) | Interne | Bloquant pour le dataset et le RAG |
| Export structuré de la RFE (Excel/CSV) | Interne | Bloquant pour RAG-structuré |
| Validation par un expert clinicien | Externe | Non bloquant pour le POC, bloquant pour la publication |

---

## 8. Risques

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| R1 | Dataset de qualité insuffisante (questions ambiguës) | Moyenne | Critique | Thomas est médecin anesthésiste, validation initiale par lui-même puis par un pair |
| R2 | Scoring trop simpliste (faux négatifs) | Haute | Moyen | Scoring multi-critères + synonymes (Epic 3) |
| R3 | Coût des runs dépasse le budget | Faible | Moyen | Dry-run pour estimer, mécanisme de budget cap |
| R4 | Pas de publication acceptée | Haute | Moyen | Cibler des venues variées (congrès + revue + preprint) |
| R5 | APIs LLM indisponibles ou instables | Faible | Bloquant | Retries, cache des réponses, tests offline avec mocks |

---

## 9. Métriques de succès

| Métrique | Cible | Timeline |
|----------|-------|----------|
| POC fonctionnel démontrable | 2+ modèles, scoring auto, résultats lisibles | 2 avril 2026 |
| Abstract soumis au congrès SFAR | 1 soumission | 21 avril 2026 |
| Dossier AMI BOAS intégrant le benchmark | 1 dossier | 11 mai 2026 |
| Publication soumise (npj Digital Medicine ou équivalent) | 1 soumission | 3 juin 2026 |
| Taille du dataset | 60+ questions | Mai 2026 |
| Nombre d'approches testées | 3+ | Juin 2026 |

---

## 10. Prochaine étape recommandée

Passer à l'**architecture système** avec le System Architect (`bmad-system-architect`) pour valider/affiner l'architecture hexagonale existante au regard des exigences formalisées dans ce PRD.

**Handoff vers :** System Architect (`bmad-system-architect`)

---

*Document généré le 2026-03-28. 23 FR + 12 NFR + 6 Epics + 22 Stories.*
*Priorités FR : 9 MUST, 9 SHOULD, 3 COULD, 0 WONT (2 ajoutées : FR-007 structured output, FR-023 plateforme QCM).*
*Priorités NFR : 7 MUST, 5 SHOULD.*

---

## 11. Perspectives post-V1 (issues de la réunion Groupe Numérique SFAR — 2026-04-02)

### Contexte

Lors de la réunion en présentiel du Groupe Numérique SFAR (02/04/2026), l'exemple d'antibioprophylaxie au format JSON a servi d'illustration concrète. Plusieurs pistes d'évolution ont émergé, au-delà du scope V1 actuel.

### Pistes identifiées

**Généralisation à d'autres RFEs SFAR**
- Notre benchmark antibio pourrait servir de pilote pour structurer l'ensemble des recommandations SFAR au format JSON
- Proposition discutée : mettre à disposition des RFEs structurées pour intégration dans l'application SFAR (contexte : les recommandations sont peu appliquées en pratique)

**MCP de recommandations nationales**
- Idée émergente : créer un MCP (Model Context Protocol) exposant les recommandations nationales de sociétés savantes (SFAR et autres) comme source de contexte pour les LLMs
- Permettrait à un modèle d'accéder aux guidelines à jour lors d'une interaction clinique

**Outils d'extraction à évaluer**
- DocuPipe (extraction structurée depuis PDF via IA) — à tester sur le free tier pour les PDFs de guidelines
  → voir note ressource : [[DocuPipe]]

**Workflow de gouvernance inspiré d'INDICATE (Boris Delange)**
- INDICATE a développé pour ses données de réanimation une approche élégante : dataset versionné sur GitHub (source de vérité) + interface Shiny déployée sur GitHub Pages (consultation sans compétences techniques) + workflow de statut par concept (`draft → pending review → approved → deprecated`)
- Application directe pour notre dataset : statut par question, interface de révision pour les cliniciens SFAR, traçabilité complète de la validation
- **Point clé :** Boris Delange travaille à généraliser ce workflow de façon agnostique à INDICATE, avec une publication/mise à disposition prévue dans 1-2 mois. À surveiller et potentiellement contacter pour collaboration.
- Argument fort pour publication : dataset consultable publiquement, méthodologie de validation transparente et reproductible

### Backlog idées (hors scope V1)

| Idée | Complexité estimée | Lien avec V1 | Statut |
|------|--------------------|--------------|--------|
| Extension à d'autres RFEs SFAR | Élevée | Architecture extensible prévue (ports & adaptateurs) | Idée |
| MCP recommandations nationales | Moyenne | Dataset JSON = brique de base | Idée |
| Intégration appli SFAR | Élevée | Dépend du format retenu par la SFAR | Idée |
| Évaluation DocuPipe pour extraction PDF | Faible | Complément/alternative au parser AC2 | À tester |
| Workflow de gouvernance dataset (inspiré INDICATE) | Moyenne | Dataset versionné déjà sur GitHub | En veille — attendre publication Boris Delange (juin 2026 ?) |
| Interface Shiny/web de consultation du dataset | Moyenne | Dépend du workflow de gouvernance | En veille |
