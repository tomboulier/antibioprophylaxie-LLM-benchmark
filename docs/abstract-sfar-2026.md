# Abstract SFAR 2026 — Brouillon

> **Limite** : 3 500 caractères espaces inclus (hors titre, auteurs, affiliations, images)
> **Statut** : Brouillon v1 — trous à compléter `[___]`

---

## Titre

Évaluation comparative de grands modèles de langage pour l'antibioprophylaxie chirurgicale en orthopédie-traumatologie : une méthode de test standardisée appliquée aux RFE SFAR 2024

---

## Corps de l'abstract

**Introduction**

Les systèmes d'intelligence artificielle (IA) tels que ChatGPT, c'est-à-dire basés sur les grands modèles de langage (LLMs pour *large language models*), sont de plus en plus envisagés comme outils d'aide à la décision clinique. Cependant, ces modèles peuvent produire des réponses incorrectes mais formulées avec assurance, un phénomène appelé « hallucination » (1). En contexte clinique, ces erreurs représentent un risque pour la sécurité des patients, notamment lorsqu'elles portent sur des posologies ou des choix de molécules (2). Leur fiabilité sur des recommandations formalisées d'experts (RFE) reste peu évaluée de manière standardisée. L'objectif de cette étude est de proposer une méthode d'évaluation reproductible et librement réutilisable pour mesurer la fiabilité de plusieurs LLM sur les RFE d'antibioprophylaxie en chirurgie et médecine interventionnelle (3), appliquée ici à l'orthopédie et à la traumatologie.

**Matériel et méthodes**

Un jeu de 23 questions/réponses standardisées (14 questions ouvertes, 9 QCMs) a été construit à partir des RFE SFAR 2024 (V2.0, 22/05/2024), couvrant la chirurgie orthopédique programmée et la traumatologie. L'ensemble des questions/réponses, le code d'évaluation et les résultats sont publiés en accès libre (4), afin de permettre leur réplication et leur extension.

Trois modèles commerciaux ont été évalués : Mistral, Claude et GPT-4. Chaque modèle a répondu à l'ensemble des questions dans des conditions identiques et reproductibles. La correction est automatisée : correspondance exacte pour les QCM, correspondance normalisée (insensible à la casse, prise en compte des synonymes DCI/noms commerciaux) pour les questions ouvertes. Les critère de jugement principal est le taux de réponses correctes (global et par type de question).

**Résultats**

[___]

| Modèle | Précision globale | Précision open | Précision QCM | Latence moy. (s) | Coût/question (USD) |
|--------|:-:|:-:|:-:|:-:|:-:|
| [___] | [___] | [___] | [___] | [___] | [___] |
| [___] | [___] | [___] | [___] | [___] | [___] |
| [___] | [___] | [___] | [___] | [___] | [___] |

[1-2 phrases de résultats narratifs : meilleur modèle, écarts observés, types de questions les plus discriminants]

**Conclusion**

[1-2 phrases sur le résultat principal]. Cette méthode d'évaluation, reproductible et librement réutilisable, peut être étendue à d'autres spécialités chirurgicales et à d'autres corpus de recommandations. Les questions, le protocole de test et les résultats complets sont disponibles publiquement pour encourager la recherche collaborative sur la fiabilité des LLM en contexte médical.

**Références**

1. Sallam M. The Clinicians' Guide to Large Language Models: A General Perspective With a Focus on Hallucinations. Interact J Med Res. 2025;14:e59823.
2. Bedi S et al. A framework to assess clinical safety and hallucination rates of LLMs for medical text summarisation. npj Digit Med. 2025;8:279.
3. SFAR, SPILF. Antibioprophylaxie en chirurgie et médecine interventionnelle. Recommandations formalisées d'experts. V2.0, 22/05/2024. Disponible sur : sfar.org
4. Disponible sur : github.com/tomboulier/antibioprophylaxie-LLM-benchmark

---

## Décompte (estimé sans les trous)

~1 700 caractères de texte fixe. Budget restant pour les résultats : ~1 800 caractères.

## Notes pour les co-auteurs

- **À relire en priorité** : les 23 questions dans `research/benchmark.md` (réponses correctes ? cas manquants en ortho/traumato ?)
- **Anonymat** : le corps du texte ne doit pas mentionner de nom de centre, de ville ou d'auteur
- **Figures possibles** (2 max) : schéma du pipeline de benchmark + tableau de résultats
