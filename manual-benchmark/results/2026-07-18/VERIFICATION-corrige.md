# Vérification du corrigé — 14 désaccords partagés

Items où **Claude ET Le Chat** donnent une réponse contraire au corrigé. Chacun
a été **recroisé avec le PDF de la RFE** ([`RFE-antibioprophylaxie-SFAR-v2.0.pdf`](../../../datasets/sfar_antibioprophylaxie/RFE-antibioprophylaxie-SFAR-v2.0.pdf)).

## Conclusion : corrigé **correct 14/14**. Ce sont les modèles qui se trompent.

Les erreurs partagées ne révèlent **pas** un défaut de la vérité terrain, mais une
limite réelle des modèles : ils donnent la « réponse plausible par défaut »
(règle générale, molécule de base) et **ratent les exceptions propres à chaque
tableau**. Aucune correction à apporter à `benchmark.json`.

| id | Question | Corrigé | Preuve RFE (tableau) | Verdict |
|----|----------|---------|------------------------|---------|
| Q04 | PTH voie antérieure + allergie | Vancomycine | Ortho (p.73‑74) : règle allergie = clindamycine, **sauf** note « PTH voie antérieure → préférer vancomycine/téicoplanine » (résistance *Cutibacterium acnes*) | ✅ corrigé |
| Q27 | Craniotomie + allergie | Clindamycine | Neuro (p.38) : craniotomie = céfazoline ; allergie « si céfazoline → clindamycine 900 mg » | ✅ corrigé |
| Q42 | Chirurgie orthognatique | Céfazoline | Stomato‑maxillo (p.43) : **Céfazoline** (alternative : Amox/Clav) | ✅ corrigé — modèles ont donné l'alternative |
| Q45 | TAVI | Amox/Clav | Cardio structurelle (p.49) : **Amox/Clav** (alt : Céfazoline **+** Amoxicilline) | ✅ corrigé — modèles ont donné une moitié du combo |
| Q131 | Fermeture FOP percutané | Amox/Clav | Même ligne que TAVI (p.49) | ✅ corrigé |
| Q63 | Vaginoplastie (affirmation de genre) | Amox/Clav | Chir. d'affirmation de genre : vaginoplastie/vestibuloplastie = **Amox/Clav** | ✅ corrigé |
| Q69 | Annexectomie coelio | Céfazoline | Gynéco annexes coelio (p.66) : annexectomie/ovariectomie/curage/omentectomie = **Céfazoline** (≠ kystectomie = pas d'ABP) | ✅ corrigé |
| Q154 | QCM : coelio gynéco SANS ABP | C (kystectomie) | Même tableau : seule la **kystectomie ovarienne** est en « pas d'ABP » | ✅ corrigé (modèles : A) |
| Q71 | Hystérectomie totale laparo | Céfoxitine | Chir. utérus (p.67) : hystérectomie **totale** = **Céfoxitine** (subtotale = Céfazoline) | ✅ corrigé |
| Q91 | Hémorroïdes | Métronidazole | Proctologie : hémorroïdes/fistule/kyste pilonidal = **Métronidazole 1 g** | ✅ corrigé |
| Q114 | Urétéroscopie | Céfazoline | Urologie voies excrétrices (p.89) : urétéroscopie = **Céfazoline** (GRADE 1) | ✅ corrigé |
| Q136 | Curage axillaire **seul** | Pas d'ABP | Sein/plastie : « curage axillaire **ou inguinal seul** → **PAS D'ABP** » (≠ tumorectomie *avec* curage = Céfazoline) | ✅ corrigé |
| Q142 | QCM : seuil Gustilo | B (2) | Traumato (p.76) : Gustilo 1 = Céfazoline ; **Gustilo 2 ou 3** = Amox/Clav → bascule à **2** | ✅ corrigé (modèles : C) |
| Q143 | QCM : plaie main jardinage | C (Pas d'ABP) | Traumato (p.77) : « **Plaie de la main**… contaminée (tellurique/fécale) → **PAS D'ABP** » (≠ parties molles *hors main* = Amox/Clav) | ✅ corrigé |

## Deux nuances de scoring

Ni le corrigé ni le modèle n'est cliniquement absurde sur ces deux items — le
scorer strict (1re intention seule) les compte faux :

- **Q42** — les modèles ont répondu **Amox/Clav**, qui est **l'alternative
  officiellement listée** à la céfazoline.
- **Q45 / Q131** — les modèles ont répondu **Céfazoline**, qui est **la moitié du
  combo alternatif** (`Céfazoline + Amoxicilline`).

→ Question ouverte pour la suite : scoring **strict** (1re intention) vs
**tolérant** (alternatives RFE acceptées). Candidat à une option du scorer.
