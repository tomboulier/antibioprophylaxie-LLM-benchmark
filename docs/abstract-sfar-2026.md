# Abstract SFAR 2026 — Brouillon

> **Limite** : 3 500 caractères espaces inclus (hors titre, auteurs, affiliations, images)
> **Statut** : Brouillon v2 — résultats Mistral Small + GPT-4o intégrés

---

## Titre

Évaluation comparative de grands modèles de langage pour l'antibioprophylaxie chirurgicale en orthopédie-traumatologie : une méthode de test standardisée appliquée aux RFE SFAR 2024

---

## Corps de l'abstract

**Introduction**

Les grands modèles de langage (LLM, tels que ChatGPT) sont envisagés comme outils d'aide à la décision clinique, mais peuvent produire des réponses incorrectes formulées avec assurance (« hallucinations ») (1), un risque pour la sécurité des patients lorsqu'il s'agit de posologies ou de choix de molécules (2). Leur fiabilité sur des recommandations formalisées d'experts (RFE) reste peu évaluée. L'objectif de cette étude est de proposer une méthode d'évaluation reproductible pour mesurer la fiabilité de plusieurs LLM sur les RFE d'antibioprophylaxie (3), appliquée ici à l'orthopédie-traumatologie.

**Matériel et méthodes**

Un jeu de 23 questions/réponses standardisées (14 questions ouvertes, 9 QCMs) a été construit à partir des RFE SFAR 2024 (V2.0, 22/05/2024), couvrant la chirurgie orthopédique programmée et la traumatologie.

Deux modèles commerciaux ont été évalués : Mistral Small (Mistral AI) et GPT-4o (OpenAI), dans des conditions identiques et reproductibles. La correction est automatisée : correspondance exacte pour les QCM, correspondance normalisée (synonymes DCI/noms commerciaux) pour les questions ouvertes. Le critère de jugement principal est le taux de réponses correctes. L'ensemble du code et des données est publié en accès libre (4).

**Résultats**

Les deux modèles obtiennent un taux de réponses correctes identique de 60 % (15/25), mais avec des profils distincts (Figure 1). Mistral Small est plus performant sur les questions ouvertes (73 % vs 67 %), tandis que GPT-4o obtient de meilleurs résultats sur les QCM (50 % vs 40 %). Les erreurs portent principalement sur les situations cliniques complexes (allergie, fractures ouvertes de haut grade) et sur les QCM impliquant des posologies ou des intervalles de réinjection.

**Discussion**

Un taux de 60 % est insuffisant pour un usage clinique sans supervision. Ce résultat, obtenu en interrogeant les modèles « à froid » (sans accès au texte des RFE), constitue un point de comparaison de base. Des techniques de réduction des hallucinations existent, notamment la génération augmentée par recherche documentaire (RAG), qui alimente le modèle avec les passages pertinents des recommandations (5), ou l'injection du texte intégral dans la requête (« long context »). L'architecture modulaire du code permet de tester ces approches sur le même jeu de questions. Le nombre limité de questions (n=23) et de modèles (n=2) constitue la principale limite de cette étude pilote.

**Conclusion**

Cette méthode d'évaluation standardisée et librement réutilisable permet de mesurer objectivement la fiabilité des LLM sur des recommandations médicales. Les questions, le code et les résultats sont disponibles publiquement (4) pour encourager la recherche collaborative.

**Références**

1. Sallam M. The Clinicians' Guide to Large Language Models: A General Perspective With a Focus on Hallucinations. Interact J Med Res. 2025;14:e59823.
2. Bedi S et al. A framework to assess clinical safety and hallucination rates of LLMs for medical text summarisation. npj Digit Med. 2025;8:279.
3. SFAR, SPILF. Antibioprophylaxie en chirurgie et médecine interventionnelle. Recommandations formalisées d'experts. V2.0, 22/05/2024. Disponible sur : sfar.org
4. Disponible sur : github.com/tomboulier/antibioprophylaxie-LLM-benchmark
5. Kohandel Gargari O et al. Enhancing medical AI with retrieval-augmented generation: A mini narrative review. Digit Health. 2025;11:20552076251337177.

---

## Décompte

~3 475 caractères (corps + références). Dans la limite.

## Notes pour les co-auteurs

- **À relire en priorité** : les 23 questions dans `research/benchmark.md` (réponses correctes ? cas manquants en ortho/traumato ?)
- **Anonymat** : le corps du texte ne doit pas mentionner de nom de centre, de ville ou d'auteur
- **Figures possibles** (2 max) : schéma du pipeline de benchmark + tableau de résultats
