# Session de brainstorm - 27 mars 2026

## Brainstorm 1 : Stratégie de démo (Reverse Brainstorming)

### Technique : "Comment rater la démo ?"

Ce qu'il faut éviter :
- Montrer du code Python ou du JSON brut
- Parler d'architecture port/adaptateur (jargon dev)
- Montrer uniquement des questions ortho/traumato ("trop niche")
- Ne pas montrer d'erreur de LLM (pas de "aha moment")

### Démo idéale

- **Format** : notebook Marimo (reproductible, peut servir de live démo)
- Partir d'une question clinique que tout MAR connaît
- Montrer **côte à côte** les réponses de 3+ modèles, et ou ils se trompent
- Le moment fort : montrer une erreur flagrante d'un LLM populaire
- Pas besoin de dire "imaginez sur les anticoagulants" : Thaïs Walter en a déjà parlé au groupe, le problème est connu
- Finir par : cette démo peut être montrée au GIHP et au comité des référentiels pour les convaincre de travailler à un jeu de questions pertinentes
- Mentionner les bénéfices collatéraux : outil de formation continue pour les médecins quand de nouvelles RFEs sortent, formation des internes

## Brainstorm 2 : Format du benchmark (Starbursting)

### QUI ?

- **Rédaction** : Thomas seul pour le POC (questions "faciles" ABP), puis experts ensuite
- **Validation** : comité des référentiels, GIHP, etc.
- **Consommateurs** : devs (tester les performances de leur outil), médecins (formation continue sur les RFEs, effet pédagogique)

### QUOI ?

- **Types de questions V1** : QCM (simple, scoring déterministe) + factuel direct (nom de molécule, posologie)
- **Vignettes cliniques** : à terme, avec des QCM pour rester scorable
- **Cas pièges** : oui, dans les métadonnées
- **Métadonnées V1** : difficulty + type de question, KISS/YAGNI, ne pas surcharger
- **Format de réponse** : lettre pour QCM, nom de molécule ou posologie pour factuel

### COMMENT ?

- **Publication** : JSON dans le repo + HuggingFace + data paper
- **Versioning** : semantic versioning pour les données + DOI via Zenodo
- **Multilingue** : pas de traduction des RFEs SFAR, la langue du dataset suit la langue des recommandations

### POURQUOI ?

- QCM d'abord car KISS, on complexifie après si besoin (YAGNI)
- JSON custom OK, format proche de MMLU pour compatibilité HuggingFace
- Pas de LLM-as-judge pour la V1

### ET SI ?

- LLM a vu les RFEs en entraînement ? Tant mieux, on verra s'ils sont meilleurs. Les vignettes cliniques viendront plus tard pour tester le "raisonnement"
- Experts pas d'accord ? Kappa inter-rater pour mesurer la concordance
- Dataset adopté par d'autres ? Le format QCM simple (question, choix, réponse, métadonnées) est déjà générique
