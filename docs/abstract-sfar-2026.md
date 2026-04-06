# Abstract SFAR 2026 — Brouillon

> **Limite** : 3 500 caractères espaces inclus (hors titre, auteurs, affiliations, images)
> **Statut** : Brouillon v2 — résultats Mistral Small + GPT-4o intégrés

---

## Titre

Évaluation comparative de grands modèles de langage pour l'antibioprophylaxie chirurgicale en orthopédie-traumatologie : une méthode de test standardisée appliquée aux RFE SFAR 2024

---

## Corps de l'abstract

**Introduction**

Les systèmes d'intelligence artificielle (IA) tels que ChatGPT, c'est-à-dire basés sur les grands modèles de langage (LLMs pour *large language models*), sont de plus en plus envisagés comme outils d'aide à la décision clinique. Cependant, ces modèles peuvent produire des réponses incorrectes mais formulées avec assurance, un phénomène appelé « hallucination » (1). En contexte clinique, ces erreurs représentent un risque pour la sécurité des patients, notamment lorsqu'elles portent sur des posologies ou des choix de molécules (2). Leur fiabilité sur des recommandations formalisées d'experts (RFE) reste peu évaluée de manière standardisée. L'objectif de cette étude est de proposer une méthode d'évaluation reproductible et librement réutilisable pour mesurer la fiabilité de plusieurs LLM sur les RFE d'antibioprophylaxie en chirurgie et médecine interventionnelle (3), appliquée ici à l'orthopédie et à la traumatologie.

**Matériel et méthodes**

Un jeu de 23 questions/réponses standardisées (14 questions ouvertes, 9 QCMs) a été construit à partir des RFE SFAR 2024 (V2.0, 22/05/2024), couvrant la chirurgie orthopédique programmée et la traumatologie.

Deux modèles commerciaux ont été évalués : Mistral Small (Mistral AI) et GPT-4o (OpenAI). Chaque modèle a répondu à l'ensemble des questions dans des conditions identiques et reproductibles. La correction est automatisée : correspondance exacte pour les QCM, correspondance normalisée (insensible à la casse, prise en compte des synonymes DCI/noms commerciaux) pour les questions ouvertes. Le critère de jugement principal est le taux de réponses correctes (global et par type de question).

L'ensemble des questions/réponses, le code d'évaluation et les résultats sont publiés en accès libre (4), afin de permettre leur réplication et leur extension.

**Résultats**

Les deux modèles obtiennent un taux de réponses correctes identique de 60 % (15/25), mais avec des profils distincts (Figure 1). Mistral Small est plus performant sur les questions ouvertes (73 % vs 67 %), tandis que GPT-4o obtient de meilleurs résultats sur les QCM (50 % vs 40 %). Les erreurs portent principalement sur les situations cliniques complexes (allergie, fractures ouvertes de haut grade) et sur les QCM impliquant des posologies ou des intervalles de réinjection. Le coût par question est 10 fois inférieur pour Mistral Small ($0,00004 vs $0,00045).

**Conclusion**

Les deux LLM évalués atteignent un taux de réponses correctes de 60 % sur les RFE d'antibioprophylaxie en orthopédie-traumatologie, ce qui souligne la nécessité d'une validation rigoureuse avant toute utilisation clinique. Cette méthode d'évaluation, reproductible et librement réutilisable, peut être étendue à d'autres spécialités chirurgicales et à d'autres corpus de recommandations. Les questions, le protocole de test et les résultats complets sont disponibles publiquement pour encourager la recherche collaborative sur la fiabilité des LLM en contexte médical.

**Références**

1. Sallam M. The Clinicians' Guide to Large Language Models: A General Perspective With a Focus on Hallucinations. Interact J Med Res. 2025;14:e59823.
2. Bedi S et al. A framework to assess clinical safety and hallucination rates of LLMs for medical text summarisation. npj Digit Med. 2025;8:279.
3. SFAR, SPILF. Antibioprophylaxie en chirurgie et médecine interventionnelle. Recommandations formalisées d'experts. V2.0, 22/05/2024. Disponible sur : sfar.org
4. Disponible sur : github.com/tomboulier/antibioprophylaxie-LLM-benchmark

---

## Décompte

~3 550 caractères (corps + références). Légèrement au-dessus de la limite de 3 500 si les références comptent. Vérifier sur la plateforme de soumission.

## Notes pour les co-auteurs

- **À relire en priorité** : les 23 questions dans `research/benchmark.md` (réponses correctes ? cas manquants en ortho/traumato ?)
- **Anonymat** : le corps du texte ne doit pas mentionner de nom de centre, de ville ou d'auteur
- **Figures possibles** (2 max) : schéma du pipeline de benchmark + tableau de résultats
