# Abstract SFAR 2026 — Brouillon

> **Limite** : 3 500 caractères espaces inclus (hors titre, auteurs, affiliations, images)
> **Statut** : Brouillon v4, résultats 3 modèles (171 questions, couverture élargie)

---

## Titre

Évaluation comparative de l'adhérence des grands modèles de langage aux recommandations formalisées d'experts de la SFAR sur l'antibioprophylaxie en chirurgie et médecine interventionnelle : une méthode de test standardisée

---

## Corps de l'abstract

**Introduction**

Les grands modèles de langage (large language models, LLM) tels que ChatGPT sont envisagés comme outils d'aide à la décision clinique. L'un des principaux obstacles à leur mise en place est le phénomène d'« hallucinations » [1], c'est-à-dire la production de réponses incorrectes formulées avec assurance. Cela représente un risque pour la sécurité des patients lorsqu'il s'agit de posologies ou de choix de molécules [2]. La fiabilité des LLM sur des recommandations formalisées d'experts (RFE) reste peu évaluée. L'objectif de cette étude est de proposer une méthode d'évaluation reproductible pour mesurer la fiabilité de plusieurs LLM sur les RFE concernant l'antibioprophylaxie en chirurgie et médecine interventionnelle, émises par la SFAR en 2024 [3].

**Matériel et méthodes**

Un jeu de 171 questions/réponses standardisées (138 questions ouvertes, 33 QCM) a été construit à partir des RFE SFAR 2024 (V2.0, 22/05/2024), couvrant l'ensemble des spécialités concernées par les recommandations.

Trois modèles commerciaux ont été évalués : Mistral Large (Mistral AI), GPT-4o (OpenAI) et Claude Sonnet 4.5 (Anthropic), dans des conditions identiques et reproductibles (Figure 1). Le code est écrit en Python 3.12 et utilise la bibliothèque LiteLLM pour interroger les modèles via les interfaces de programmation de chaque fournisseur. La correction est automatisée : correspondance exacte pour les QCM, correspondance normalisée (insensibilité aux accents et aux majuscules/minuscules) pour les questions ouvertes. Le critère de jugement principal est le taux de réponses correctes. L'ensemble du code et des données est publié en accès libre [4].

**Résultats**

Les trois modèles obtiennent des taux de réponses correctes contrastés (Figure 2) : GPT-4o 71 % (122/171), Mistral Large 62 % (106/171) et Claude Sonnet 61 % (104/171). GPT-4o devance les deux autres modèles à la fois sur les QCM (76 % vs 67 % et 73 %) et sur les questions ouvertes (70 % vs 61 % et 58 %). L'exécution complète (513 requêtes) a duré environ 19 minutes sur un ordinateur portable personnel.

**Discussion**

Un taux plafonnant à 71 % reste insuffisant pour un usage clinique sans supervision. Ces résultats, obtenus en interrogeant les modèles « à froid » (sans accès au texte des RFE), constituent un point de comparaison de base. Des techniques de réduction des hallucinations existent, notamment la génération augmentée par recherche documentaire (retrieval augmented generation, RAG), qui alimente le modèle avec les passages pertinents des recommandations [5], ou l'injection du texte intégral dans la requête. L'architecture modulaire du code permet de tester ces approches sur le même jeu de questions.

**Conclusion**

Trois modèles d'IA commerciaux ont été évalués sur 171 questions d'antibioprophylaxie issues des RFE SFAR 2024 : le meilleur (GPT-4o) atteint 71 % de réponses correctes lorsqu'il est interrogé sans accès au texte des recommandations. Ce jeu de test, publié en accès libre [4], fournit une base de comparaison pour évaluer les approches augmentées comme le RAG, susceptibles d'améliorer leur fiabilité.

**Références**

1. Sallam M. Interact J Med Res. 2025;14:e59823.
2. Bedi S et al. npj Digit Med. 2025;8:279.
3. SFAR, SPILF. RFE Antibioprophylaxie. V2.0, 22/05/2024. sfar.org
4. Dépôt public (code et données). Lien communiqué après évaluation pour garantir l'anonymat.
5. Kohandel Gargari O et al. Digit Health. 2025;11:20552076251337177.

---

## Figures

**Figure 1.** Méthode d'évaluation. Un questionnaire standardisé de questions est soumis à trois grands modèles de langage, puis corrigé automatiquement par comparaison aux réponses attendues issues des recommandations formalisées d'experts de la SFAR sur l'antibioprophylaxie en chirurgie et médecine interventionnelle.

![Figure 1 — Méthode d'évaluation](pipeline_benchmark.png)

**Figure 2.** Taux de réponses correctes par modèle et par type de question (questions ouvertes et QCM).

![Figure 2 — Résultats comparatifs](accuracy_comparison.png)
