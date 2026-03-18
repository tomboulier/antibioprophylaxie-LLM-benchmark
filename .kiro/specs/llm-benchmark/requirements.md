# Requirements Document

## Introduction

`medical-llm-benchmark` est un cadre d'évaluation (*framework*) libre (*open source*) et reproductible pour évaluer des grands modèles de langage (*LLM*) sur des recommandations médicales issues de sociétés savantes. Il permet de croiser plusieurs **approches** (RAG, MCP, contexte long, etc.) avec plusieurs **modèles** (Mistral, Claude, GPT-4o, etc.) sur un jeu de données (*dataset*) de questions standardisées (elles aussi sous licence libre), et de mesurer objectivement leur précision, leur sourçage et leurs métriques opérationnelles.

Le premier cas d'usage concret est le banc d'essai des recommandations formalisée d'experts (RFE) de la SFAR concernant l'antibioprophylaxie chirurgicale (publiées en 2024), mais l'architecture doit permettre d'ajouter d'autres domaines médicaux et d'autres sociétés savantes sans modifier le cœur du cadre d'évaluation.

L'objectif à terme est de fournir aux sociétés savantes un outil standardisé pour évaluer les applications IA qui prétendent s'appuyer sur leurs recommandations, et de publier les résultats de manière reproductible.

## Glossaire

- **Cadre d'évaluation** (*framework*) : le système `medical-llm-benchmark` dans son ensemble.
- **Banc d'essai** (*benchmark*) : protocole d'évaluation comparative d'approches et de grands modèles de langage sur un jeu de données standardisé.
- **Jeu de données** (*dataset*) : ensemble de questions standardisées avec réponses attendues, associé à un domaine médical.
- **Question** : unité d'évaluation, de type ouvert ou QCM, avec une réponse attendue et une source de référence.
- **Approche** : stratégie d'accès à la connaissance médicale (ex : RAG PDF, contexte long, MCP). Implémentée comme un adaptateur.
- **Grand modèle de langage** (*LLM, Large Language Model*) : modèle d'IA interrogé (ex : Mistral-7B, claude-sonnet, gpt-4o). Indépendant de l'approche.
- **Exécution** (*run*) : lancement du banc d'essai pour une combinaison (Approche × Grand modèle de langage) sur un Jeu de données.
- **Résultat** : sortie structurée d'une Exécution, contenant les réponses, l'évaluation et les métriques.
- **Évaluateur** (*scorer*) : composant qui évalue une réponse par rapport à la réponse attendue.
- **Métrique** : mesure collectée lors d'une Exécution (précision, latence, jetons, coût, sourçage, etc.).
- **Rapport** : synthèse comparative de plusieurs Exécutions, exportable en JSON/CSV.
- **Adaptateur** (*adapter*) : implémentation concrète d'une Approche ou d'un export de Résultats, conforme à un port défini.
- **Port** : interface abstraite définissant le contrat d'un composant extensible.
- **Jeton** (*token*) : unité de traitement d'un Grand modèle de langage, utilisée pour mesurer la consommation et estimer les coûts.
- **Sourçage** : capacité d'une réponse à citer explicitement la recommandation de référence.
- **SFAR** : Société Française d'Anesthésie et de Réanimation.
- **RFE** : Recommandations Formalisées d'Experts.

## Requirements

### Requirement 1 : Jeu de données standardisé

**User Story:** En tant que chercheur, je veux définir un jeu de données (*dataset*) de questions standardisées avec réponses attendues, afin de disposer d'une base d'évaluation reproductible et partageable.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL accepter un Jeu de données au format JSON contenant des questions de type ouvert et de type QCM.
2. THE Cadre d'évaluation SHALL valider la structure de chaque Question (présence des champs : id, type, question, réponse, source).
3. IF un Jeu de données contient une Question dont la structure est invalide, THEN THE Cadre d'évaluation SHALL rejeter le Jeu de données et retourner une liste des erreurs de validation.
4. THE Cadre d'évaluation SHALL permettre de définir plusieurs Jeux de données indépendants correspondant à des domaines médicaux distincts.
5. WHERE un Jeu de données contient des questions de type QCM, THE Cadre d'évaluation SHALL stocker les choix de réponse (A, B, C, D) dans la Question.

---

### Requirement 2 : Architecture extensible par ports et adaptateurs

**User Story:** En tant que contributeur à ce projet libre, je veux que le cadre d'évaluation soit structuré autour de ports et d'adaptateurs, afin de pouvoir ajouter de nouvelles approches, de nouveaux grands modèles de langage ou de nouveaux formats d'export sans modifier le cœur du système.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL définir un Port d'Approche spécifiant le contrat minimal qu'un Adaptateur doit implémenter pour répondre à une Question.
2. THE Cadre d'évaluation SHALL définir un Port de Grand modèle de langage spécifiant le contrat d'appel (entrée : invite, sortie : texte + métriques brutes).
3. THE Cadre d'évaluation SHALL définir un Port d'Export spécifiant le contrat de sérialisation d'un Résultat.
4. WHEN une nouvelle Approche est ajoutée, THE Cadre d'évaluation SHALL l'intégrer sans modification du code du moteur du banc d'essai.
5. WHEN un nouveau Jeu de données est ajouté, THE Cadre d'évaluation SHALL l'intégrer sans modification du code du moteur du banc d'essai.
6. WHERE une Approche est configurable par des paramètres simples, THE Cadre d'évaluation SHALL permettre sa déclaration via un fichier YAML.
7. WHERE une Approche nécessite une logique personnalisée, THE Cadre d'évaluation SHALL permettre son implémentation via un Adaptateur Python conforme au Port d'Approche.

---

### Requirement 3 : Exécution du banc d'essai

**User Story:** En tant que chercheur, je veux lancer un banc d'essai en croisant des approches et des grands modèles de langage sur un jeu de données, afin d'obtenir des résultats comparables et reproductibles.

#### Acceptance Criteria

1. WHEN une Exécution est lancée, THE Cadre d'évaluation SHALL traiter chaque combinaison (Approche × Grand modèle de langage) sur les Questions sélectionnées du Jeu de données, l'ensemble des Questions étant la sélection par défaut.
2. THE Cadre d'évaluation SHALL associer à chaque Exécution un identifiant unique et un horodatage.
3. THE Cadre d'évaluation SHALL enregistrer pour chaque Question d'une Exécution : la réponse obtenue, l'évaluation, et l'ensemble des métriques collectées pour cette Exécution.
4. IF une erreur survient lors de l'interrogation d'un Grand modèle de langage pour une Question, THEN THE Cadre d'évaluation SHALL enregistrer l'erreur dans le Résultat et poursuivre l'Exécution pour les Questions suivantes.
5. THE Cadre d'évaluation SHALL permettre de filtrer les Questions à exécuter par identifiant.
6. THE Cadre d'évaluation SHALL permettre de lister les Approches, Grands modèles de langage, Jeux de données et Métriques disponibles via une commande en ligne de commande.
7. WHILE une Exécution est en cours, THE Cadre d'évaluation SHALL afficher la progression question par question.

---

### Requirement 4 : Notation déterministe

**User Story:** En tant que chercheur, je veux que les réponses soient évaluées de manière déterministe et reproductible, afin que les résultats soient comparables entre exécutions et publiables.

#### Acceptance Criteria

1. WHEN une Question de type ouvert est évaluée, THE Évaluateur SHALL comparer la réponse obtenue à la réponse attendue après normalisation (casse, espaces, ponctuation).
2. WHEN une Question de type QCM est évaluée, THE Évaluateur SHALL extraire la lettre de réponse (A–D) de la réponse obtenue et la comparer à la lettre attendue.
3. WHEN une réponse attendue contient plusieurs molécules séparées par "+", THE Évaluateur SHALL vérifier que chaque molécule est présente dans la réponse obtenue.
4. WHEN la réponse attendue est "Non", THE Évaluateur SHALL contraindre la réponse du grand modèle de langage à "Oui" ou "Non" via l'invite, puis appliquer une comparaison exacte normalisée.
5. THE Évaluateur SHALL être extensible : WHEN un nouveau type de Question est ajouté, THE Cadre d'évaluation SHALL permettre d'associer un Évaluateur dédié sans modifier les Évaluateurs existants.
6. FOR ALL Questions d'un Jeu de données, THE Évaluateur SHALL produire une note binaire (correct / incorrect) et une note agrégée (précision en pourcentage) par Exécution.

---

### Requirement 5 : Métriques opérationnelles

**User Story:** En tant que chercheur, je veux collecter des métriques opérationnelles pour chaque Exécution, afin de comparer les approches sur des critères au-delà de la précision.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL collecter la latence (en secondes) pour chaque Question d'une Exécution.
2. THE Cadre d'évaluation SHALL collecter le nombre de jetons (*tokens*, invite et complétion séparément) pour chaque Question d'une Exécution, lorsque le Grand modèle de langage expose cette information.
3. THE Cadre d'évaluation SHALL calculer le coût estimé (en euros ou dollars) pour chaque Question d'une Exécution, sur la base des tarifs déclarés du Grand modèle de langage.
4. THE Cadre d'évaluation SHALL estimer l'empreinte carbone (en grammes de CO2 équivalent) pour chaque Exécution, sur la base de la consommation énergétique estimée et de l'intensité carbone du réseau électrique.
5. IF un Grand modèle de langage ne fournit pas une métrique donnée, THEN THE Cadre d'évaluation SHALL enregistrer la valeur comme absente (null) sans interrompre l'Exécution.
6. THE Cadre d'évaluation SHALL permettre d'ajouter de nouvelles Métriques via le Port de Grand modèle de langage sans modifier le moteur du banc d'essai.

---

### Requirement 6 : Évaluation du sourçage

**User Story:** En tant que chercheur, je veux évaluer si les réponses des grands modèles de langage citent leurs sources, afin de mesurer la fiabilité et la traçabilité des réponses dans un contexte médical.

#### Acceptance Criteria

1. WHEN une réponse est évaluée, THE Évaluateur SHALL détecter la présence d'une référence explicite à une source dans le texte de la réponse.
2. WHEN une référence est détectée dans une réponse, THE Évaluateur SHALL vérifier si cette référence correspond à la source attendue déclarée dans la Question.
3. THE Cadre d'évaluation SHALL calculer un taux de sourçage (pourcentage de réponses contenant une référence) par Exécution.
4. THE Cadre d'évaluation SHALL calculer un taux de sourçage correct (pourcentage de réponses dont la référence correspond à la source attendue) par Exécution.
5. IF une Question ne déclare pas de source attendue, THEN THE Évaluateur SHALL évaluer uniquement la présence d'une référence, sans vérifier sa correction.

---

### Requirement 7 : Export et reproductibilité des résultats

**User Story:** En tant que chercheur, je veux exporter les résultats dans des formats standards et reproductibles, afin de partager les données et de permettre leur réplication par d'autres équipes.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL exporter chaque Résultat d'Exécution au format JSON structuré, incluant les métadonnées de l'Exécution (jeu de données, approche, grand modèle de langage, horodatage, version du cadre d'évaluation).
2. THE Cadre d'évaluation SHALL exporter un Rapport comparatif de plusieurs Exécutions au format CSV.
3. THE Cadre d'évaluation SHALL inclure dans chaque Résultat les paramètres complets de l'Exécution (version du jeu de données, identifiant de l'approche, identifiant du grand modèle de langage, paramètres de configuration).
4. FOR ALL Exécutions lancées avec les mêmes paramètres et le même jeu de données, THE Cadre d'évaluation SHALL produire des Résultats dont le schéma JSON est identique.
5. THE Cadre d'évaluation SHALL permettre d'ajouter de nouveaux formats d'export via le Port d'Export sans modifier le moteur du banc d'essai.

---

### Requirement 8 : Interface en ligne de commande

**User Story:** En tant que chercheur, je veux une interface en ligne de commande (*CLI*) claire et documentée pour lancer des bancs d'essai et analyser les résultats, afin de pouvoir reproduire les expériences facilement.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL exposer une commande pour lancer une Exécution avec les paramètres : jeu de données, approche(s), grand(s) modèle(s) de langage, et filtre de questions.
2. THE Cadre d'évaluation SHALL exposer une commande pour lister les approches disponibles.
3. THE Cadre d'évaluation SHALL exposer une commande pour lister les grands modèles de langage disponibles.
4. THE Cadre d'évaluation SHALL exposer une commande pour lister les jeux de données disponibles.
5. THE Cadre d'évaluation SHALL exposer une commande pour lister les métriques disponibles.
6. THE Cadre d'évaluation SHALL exposer une commande pour lister les Exécutions passées et les Rapports générés.
7. THE Cadre d'évaluation SHALL exposer une commande pour agréger et comparer des Résultats existants.
8. IF un paramètre obligatoire est absent ou invalide, THEN THE Cadre d'évaluation SHALL afficher un message d'erreur explicite et retourner un code de sortie non nul.

---

### Requirement 9 : Cas d'usage SFAR antibioprophylaxie

**User Story:** En tant que membre de la SFAR, je veux un jeu de données de questions sur les recommandations d'antibioprophylaxie chirurgicale (RFE 2024), afin de disposer d'un premier banc d'essai concret et publiable.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL inclure un Jeu de données SFAR contenant au minimum 50 Questions couvrant un large spectre de spécialités chirurgicales.
2. THE Jeu de données SFAR SHALL inclure des Questions de type ouvert et de type QCM.

---

### Requirement 10 : Exploration interactive et reproductible des résultats

**User Story:** En tant que chercheur, je veux explorer et visualiser les résultats d'un banc d'essai de manière interactive et reproductible, afin de pouvoir partager mes analyses et permettre à d'autres équipes de les reproduire exactement.

#### Acceptance Criteria

1. THE Cadre d'évaluation SHALL permettre d'explorer les Résultats d'Exécutions de manière interactive, sans nécessiter de modifier le code source pour changer les paramètres de visualisation.
2. THE Cadre d'évaluation SHALL garantir que toute analyse interactive est reproductible : exécutée dans le même environnement avec les mêmes données, elle produit les mêmes sorties.
3. THE Cadre d'évaluation SHALL permettre de partager une analyse sous forme d'un fichier unique versionnable.
4. IF plusieurs Exécutions sont disponibles, THE Cadre d'évaluation SHALL permettre de les comparer visuellement dans l'interface interactive.
