# Benchmark Antibioprophylaxie SFAR

> Jeu de questions standardisé pour évaluer tout système (RAG, MCP, chatbot, LLM)
> sur les recommandations d'antibioprophylaxie chirurgicale (RFE SFAR 2024).
>
> **Source** : RFE SFAR 2024 (V2.0 du 22/05/2024)
> **Auteur initial** : Claude (à valider/corriger par un médecin)
> **Date** : 2026-03-11

## Format des réponses attendues

Pour les questions ouvertes, la réponse attendue est :
- Un **nom de molécule** (ex : `Céfazoline`, `Amoxicilline/Clavulanate`)
- `Pas d'antibioprophylaxie` (pas d'ABP recommandée pour cette intervention)
- `Hors périmètre` (situation non couverte par les RFE SFAR 2024)

Pour les QCM, une seule réponse correcte (lettre).

---

## Questions ouvertes

### PTH standard

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie recommandez-vous pour une prothèse totale de hanche ?
- **réponse** : Céfazoline

### Arthroscopie genou diagnostique

- **type** : open
- **question** : Quelle est la recommandation d'antibioprophylaxie pour une arthroscopie diagnostique du genou sans mise en place de matériel ?
- **réponse** : Pas d'antibioprophylaxie

### PTG allergie bêtalactamines

- **type** : open
- **question** : Un patient allergique aux bêtalactamines doit bénéficier d'une prothèse de genou. Quelle molécule en première intention ?
- **réponse** : Clindamycine

### PTH voie antérieure allergie

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une prothèse de hanche par voie antérieure chez un patient allergique aux bêtalactamines ?
- **réponse** : Vancomycine

### Fracture ouverte Gustilo 2

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une fracture ouverte de jambe Gustilo 2 ?
- **réponse** : Amoxicilline/Clavulanate

### Fixateur externe fracture fermée

- **type** : open
- **question** : Quelle est la recommandation d'antibioprophylaxie pour la pose d'un fixateur externe sur une fracture fermée ?
- **réponse** : Pas d'antibioprophylaxie

### Arthrodèse lombaire instrumentée

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une arthrodèse lombaire instrumentée en un temps ?
- **réponse** : Céfazoline

### Parage morsure

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour le parage chirurgical d'une morsure ?
- **réponse** : Amoxicilline/Clavulanate

### Écrasement main > 2h

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour un écrasement complexe de la main nécessitant une chirurgie de plus de 2 heures ?
- **réponse** : Amoxicilline/Clavulanate

### Plaie agricole cuisse

- **type** : open
- **question** : Quelle molécule d'antibioprophylaxie pour une plaie de cuisse par accident agricole, susceptible d'être contaminée par des germes telluriques ?
- **réponse** : Amoxicilline/Clavulanate

### Plaie simple mollet

- **type** : open
- **question** : Quelle est la recommandation d'antibioprophylaxie pour le parage d'une plaie simple du mollet ?
- **réponse** : Pas d'antibioprophylaxie

### Fracture ouverte Gustilo 3 allergie

- **type** : open
- **question** : Un patient allergique aux pénicillines présente une fracture ouverte Gustilo 3. Quelle(s) molécule(s) d'antibioprophylaxie ?
- **réponse** : Clindamycine + Gentamicine

### Ablation matériel ostéosynthèse MI

- **type** : open
- **question** : Quelle est la recommandation d'antibioprophylaxie pour l'ablation de matériel d'ostéosynthèse au membre inférieur ?
- **réponse** : Pas d'antibioprophylaxie

---

## QCM

### PTG première intention

- **type** : qcm
- **question** : Quelle molécule est recommandée en première intention pour l'antibioprophylaxie d'une prothèse totale de genou ?
- **choix** :
  - A. Amoxicilline/Clavulanate
  - B. Céfazoline
  - C. Clindamycine
  - D. Vancomycine
- **réponse** : B

### Intervention sans ABP

- **type** : qcm
- **question** : Parmi ces interventions, laquelle ne nécessite PAS d'antibioprophylaxie ?
- **choix** :
  - A. Prothèse d'épaule
  - B. Cimentoplastie vertébrale
  - C. Ablation de matériel d'ostéosynthèse du fémur
  - D. Arthroscopie du genou avec mise en place de matériel
- **réponse** : C

### PTG allergie alternative

- **type** : qcm
- **question** : En cas d'allergie aux bêtalactamines, quelle est l'alternative de première intention pour l'antibioprophylaxie d'une prothèse de genou ?
- **choix** :
  - A. Gentamicine
  - B. Vancomycine
  - C. Clindamycine
  - D. Métronidazole
- **réponse** : C

### Seuil Gustilo changement molécule

- **type** : qcm
- **question** : À partir de quel stade de Gustilo la molécule d'antibioprophylaxie change-t-elle (passage de la Céfazoline à l'Amoxicilline/Clavulanate) ?
- **choix** :
  - A. Gustilo 1
  - B. Gustilo 2
  - C. Gustilo 3
  - D. Pas de changement, c'est toujours la Céfazoline
- **réponse** : B

### Réinjection Augmentin

- **type** : qcm
- **question** : À quel intervalle doit-on réinjecter l'Amoxicilline/Clavulanate en antibioprophylaxie ?
- **choix** :
  - A. Toutes les 2h
  - B. Toutes les 4h
  - C. Toutes les 6h
  - D. Pas de réinjection
- **réponse** : A

### Plaie jardinage main

- **type** : qcm
- **question** : Un patient se présente avec une plaie de la main par accident de jardinage, susceptible de contamination tellurique. Quelle est la recommandation ?
- **choix** :
  - A. Céfazoline 2g IVL
  - B. Amoxicilline/Clavulanate 2g IVL
  - C. Pas d'antibioprophylaxie recommandée
  - D. Clindamycine 900mg IVL
- **réponse** : C

### Écrasement main allergie

- **type** : qcm
- **question** : Quelle est l'alternative en cas d'allergie aux pénicillines pour un traumatisme complexe de la main (écrasement) ?
- **choix** :
  - A. Clindamycine seule
  - B. Vancomycine seule
  - C. Céfazoline + Gentamicine
  - D. Clindamycine + Gentamicine
- **réponse** : C

### Arthroscopie avec/sans matériel

- **type** : qcm
- **question** : Deux patients doivent bénéficier d'une arthroscopie de genou : l'un avec mise en place d'une ancre, l'autre sans matériel. Quelle est la bonne conduite ?
- **choix** :
  - A. Antibioprophylaxie pour les deux
  - B. Antibioprophylaxie uniquement pour celui avec matériel
  - C. Pas d'antibioprophylaxie pour les deux
  - D. Antibioprophylaxie uniquement pour celui sans matériel
- **réponse** : B

### Appendicectomie hors périmètre

- **type** : qcm
- **question** : Quelle antibioprophylaxie pour une appendicectomie ?
- **choix** :
  - A. Céfazoline 2g IVL
  - B. Amoxicilline/Clavulanate 2g IVL
  - C. Pas d'antibioprophylaxie recommandée
  - D. Hors périmètre de ces recommandations
- **réponse** : D
