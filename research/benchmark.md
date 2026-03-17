# Benchmark Antibioprophylaxie SFAR

> Jeu de questions standardisé pour évaluer tout système (RAG, MCP, chatbot, LLM)
> sur les recommandations d'antibioprophylaxie chirurgicale (RFE SFAR 2024).
>
> **Source** : RFE SFAR 2024 (V2.0 du 22/05/2024)
> **Périmètre** : Chirurgie orthopédique programmée + Traumatologie (47 interventions)
> **Auteur initial** : Claude (à valider/corriger par un médecin)
> **Date** : 2026-03-11

## Format des réponses attendues

Pour les questions ouvertes, la réponse attendue est :
- Un **nom de molécule** (ex : `Céfazoline`)
- Ou bien `Non` (pas d'antibioprophylaxie recommandée)

Pour les QCM, une seule réponse correcte (lettre).

---

## Questions ouvertes

### Q01 — Protocole standard PTH

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie recommandez-vous pour une prothèse totale de hanche ?
- **réponse** : Céfazoline
- **source** : ortho-prog-mi-prothese-hanche-genou

### Q02 — Arthroscopie diagnostique

- **type** : open
- **question** : Faut-il prescrire une antibioprophylaxie pour une arthroscopie diagnostique du genou sans mise en place de matériel ?
- **réponse** : Non
- **source** : ortho-prog-mi-arthroscopie-sans-materiel

### Q03 — Allergie PTH

- **type** : open
- **question** : Un patient allergique aux bêtalactamines doit bénéficier d'une prothèse de hanche. Quelle molécule en première intention ?
- **réponse** : Clindamycine
- **source** : ortho-prog-mi-prothese-hanche-genou

### Q04 — Allergie PTH voie antérieure

- **type** : open
- **question** : Pour une prothèse de hanche par voie antérieure chez un patient allergique aux bêtalactamines, faut-il préférer la clindamycine ou la vancomycine ?
- **réponse** : Vancomycine
- **source** : ortho-prog-mi-prothese-hanche-genou (note)

### Q05 — Fracture ouverte Gustilo 2

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une fracture ouverte de jambe Gustilo 2 ?
- **réponse** : Amoxicilline/Clavulanate
- **source** : trauma-fracture-ouverte-gustilo-2-3

### Q06 — Fracture fermée fixateur externe

- **type** : open
- **question** : Faut-il une antibioprophylaxie pour la pose d'un fixateur externe sur une fracture fermée ?
- **réponse** : Non
- **source** : trauma-fracture-fermee-fixateur-externe

### Q07 — Rachis instrumenté

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une arthrodèse lombaire instrumentée en un temps ?
- **réponse** : Céfazoline
- **source** : ortho-prog-rachis-instrumentee-1-temps

### Q08 — Rachis sans matériel

- **type** : open
- **question** : Faut-il une antibioprophylaxie pour une chirurgie du rachis sans pose de matériel (par ex. hernie discale) ?
- **réponse** : Non
- **source** : ortho-prog-rachis-sans-materiel

### Q09 — Morsure

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour le parage chirurgical d'une morsure ?
- **réponse** : Amoxicilline/Clavulanate
- **source** : trauma-morsure

### Q10 — Traumatisme complexe main

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour un écrasement complexe de la main nécessitant une chirurgie de plus de 2 heures ?
- **réponse** : Amoxicilline/Clavulanate
- **source** : trauma-main-complexe

### Q11 — Plaie tellurique

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une plaie de cuisse par accident agricole, susceptible d'être contaminée par des germes telluriques ?
- **réponse** : Amoxicilline/Clavulanate
- **source** : trauma-plaie-contaminee

### Q12 — Plaie simple parties molles

- **type** : open
- **question** : Faut-il une antibioprophylaxie pour le parage d'une plaie simple du mollet ?
- **réponse** : Non
- **source** : trauma-plaie-simple

### Q13 — Allergie Gustilo 3

- **type** : open
- **question** : Un patient allergique aux pénicillines présente une fracture ouverte Gustilo 3. Quelle(s) molécule(s) d'antibioprophylaxie ?
- **réponse** : Clindamycine + Gentamicine
- **source** : trauma-fracture-ouverte-gustilo-2-3

### Q14 — Ablation matériel membre inférieur

- **type** : open
- **question** : Faut-il une antibioprophylaxie pour l'ablation de matériel d'ostéosynthèse au membre inférieur ?
- **réponse** : Non
- **source** : ortho-prog-mi-ablation-materiel

---

## QCM

### Q15 — Molécule PTG (QCM)

- **type** : qcm
- **question** : Quelle molécule est recommandée en première intention pour l'antibioprophylaxie d'une prothèse totale de genou ?
- **choix** :
  - A. Amoxicilline/Clavulanate
  - B. Céfazoline
  - C. Clindamycine
  - D. Vancomycine
- **réponse** : B
- **source** : ortho-prog-mi-prothese-hanche-genou

### Q16 — Dose Céfazoline (QCM)

- **type** : qcm
- **question** : Quelle est la dose initiale de Céfazoline recommandée en antibioprophylaxie en chirurgie orthopédique ?
- **choix** :
  - A. 1g IVL
  - B. 2g IVL
  - C. 3g IVL
  - D. 20 mg/kg IVL
- **réponse** : B
- **source** : ortho-prog-mi-prothese-hanche-genou

### Q17 — Pas d'antibioprophylaxie (QCM)

- **type** : qcm
- **question** : Parmi ces interventions, laquelle ne nécessite PAS d'antibioprophylaxie ?
- **choix** :
  - A. Prothèse d'épaule
  - B. Arthrodèse lombaire instrumentée
  - C. Ablation de matériel d'ostéosynthèse du fémur
  - D. Arthroscopie du genou avec pose d'ancre
- **réponse** : C
- **source** : ortho-prog-mi-ablation-materiel

### Q18 — Allergie bêtalactamines (QCM)

- **type** : qcm
- **question** : En cas d'allergie aux bêtalactamines, quelle est l'alternative de première intention pour l'antibioprophylaxie d'une prothèse de hanche ?
- **choix** :
  - A. Gentamicine
  - B. Vancomycine
  - C. Clindamycine
  - D. Métronidazole
- **réponse** : C
- **source** : ortho-prog-mi-prothese-hanche-genou

### Q19 — Gustilo classification (QCM)

- **type** : qcm
- **question** : À partir de quel stade de Gustilo la molécule d'antibioprophylaxie change-t-elle (passage de la Céfazoline à l'Amoxicilline/Clavulanate) ?
- **choix** :
  - A. Gustilo 1
  - B. Gustilo 2
  - C. Gustilo 3
  - D. Pas de changement, c'est toujours la Céfazoline
- **réponse** : B
- **source** : trauma-fracture-ouverte-gustilo-1, trauma-fracture-ouverte-gustilo-2-3

### Q20 — Réinjection Amoxicilline/Clavulanate (QCM)

- **type** : qcm
- **question** : À quel intervalle doit-on réinjecter l'Amoxicilline/Clavulanate en antibioprophylaxie ?
- **choix** :
  - A. Toutes les 2h
  - B. Toutes les 4h
  - C. Toutes les 6h
  - D. Pas de réinjection
- **réponse** : A
- **source** : trauma-fracture-ouverte-gustilo-2-3

### Q21 — Plaie main tellurique (QCM)

- **type** : qcm
- **question** : Un patient se présente avec une plaie de la main par accident de jardinage, susceptible de contamination tellurique. Quelle est la recommandation ?
- **choix** :
  - A. Céfazoline 2g IVL
  - B. Amoxicilline/Clavulanate 2g IVL
  - C. Pas d'antibioprophylaxie recommandée
  - D. Clindamycine 900mg IVL
- **réponse** : C
- **source** : trauma-main-plaie-contaminee

### Q22 — Allergie trauma complexe main (QCM)

- **type** : qcm
- **question** : Quelle est l'alternative en cas d'allergie aux pénicillines pour un traumatisme complexe de la main (écrasement) ?
- **choix** :
  - A. Clindamycine seule
  - B. Vancomycine seule
  - C. Céfazoline + Gentamicine
  - D. Clindamycine + Gentamicine
- **réponse** : C
- **source** : trauma-main-complexe

### Q23 — Distinction matériel / sans matériel (QCM)

- **type** : qcm
- **question** : Deux patients doivent bénéficier d'une arthroscopie de genou : l'un avec mise en place d'une ancre, l'autre sans matériel. Quelle est la bonne conduite ?
- **choix** :
  - A. Antibioprophylaxie pour les deux
  - B. Antibioprophylaxie uniquement pour celui avec matériel
  - C. Pas d'antibioprophylaxie pour les deux
  - D. Antibioprophylaxie uniquement pour celui sans matériel
- **réponse** : B
- **source** : ortho-prog-mi-arthroscopie-avec-materiel, ortho-prog-mi-arthroscopie-sans-materiel
