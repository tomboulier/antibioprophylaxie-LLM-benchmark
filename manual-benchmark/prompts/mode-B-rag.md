<!--
prompt_version: 2.0.0
mode: B (RAG fourni — le PDF des RFE est joint en pièce jointe)
schema_version: 2 (sortie avec champs de traçabilité)
Voir CHANGELOG.md pour l'historique.
-->

# Prompt — Mode B (RFE fournie en pièce jointe)

> **Comment l'utiliser** : copiez tout le bloc ci-dessous (entre les lignes
> `─────`) dans la fenêtre de discussion, et joignez **deux fichiers** :
> 1. le PDF des RFE (`datasets/sfar_antibioprophylaxie/RFE-antibioprophylaxie-SFAR-v2.0.pdf`) ;
> 2. `questions.json` (ou collez `questions.md`).
> Récupérez le bloc JSON renvoyé et enregistrez-le dans `results/`.

─────────────────────────────────────────────────────────────────────────────

Tu es un **expert en antibioprophylaxie chirurgicale**. Je te joins **deux
documents** :
1. le **PDF des RFE SFAR 2024** sur l'antibioprophylaxie en chirurgie et médecine
   interventionnelle (le document de référence) ;
2. une liste de **questions** (`questions.json`, ou liste `questions.md` collée
   ci-dessous). Chaque question a un `id`, un `type` (`open` ou `mcq`), un
   énoncé, et pour les `mcq` des propositions `A`/`B`/`C`/`D`.

**Fonde tes réponses sur le PDF des RFE fourni.** Consulte les tableaux
correspondant à chaque spécialité et applique la recommandation. Fais attention
aux **exceptions de tableau** (ex. voie d'abord, patient allergique, geste isolé
vs associé, forme totale vs partielle). En cas d'ambiguïté, retiens ce que dit
le document.

## Règles de réponse

**Questions ouvertes (`type` = `open`)** — réponds par l'un de ces formats, et
rien d'autre :
- le **nom de la ou des molécules** (ex. `Céfazoline`, `Amoxicilline/Clavulanate`,
  `Clindamycine + Gentamicine`) ;
- `Pas d'antibioprophylaxie` si le document n'en recommande aucune ;
- `Hors périmètre` si la situation n'est pas couverte par le document.

Donne la molécule de **première intention** (pas l'alternative). N'ajoute ni
posologie, ni voie, ni justification, ni durée.

**Questions à choix multiples (`type` = `mcq`)** — réponds uniquement par la
**lettre** : `A`, `B`, `C` ou `D`.

## Format de sortie (IMPORTANT)

Aucune explication. Réponds **uniquement** par un **bloc de code JSON** conforme
à ce schéma :

```json
{
  "modele": "<nom exact de l'outil que tu es>",
  "date": "<date du jour AAAA-MM-JJ>",
  "prompt_version": "2.0.0",
  "mode": "B",
  "dataset_version": "<recopie le champ 'version' de questions.json, ou 'inconnu'>",
  "reponses": [
    { "id": "Q01", "reponse": "Céfazoline" },
    { "id": "Q02", "reponse": "Pas d'antibioprophylaxie" }
  ]
}
```

Contraintes :
- un objet par question, dans le **même ordre** que les questions ;
- `id` exactement identique à celui de la question ;
- `reponse` = chaîne (molécule, mention spéciale, ou lettre pour les `mcq`) ;
- **autant d'éléments que de questions** ;
- recopie `prompt_version`, `mode` et `dataset_version` tels quels.

**Si la réponse est trop longue pour un seul message** : découpe en plusieurs
blocs JSON successifs couvrant des plages d'`id` consécutives (ex. Q01–Q40, puis
Q41–Q80…). Chaque bloc reprend les mêmes champs de tête ; je concaténerai les
tableaux `reponses`. Ne t'arrête pas avant d'avoir couvert **toutes** les
questions.

─────────────────────────────────────────────────────────────────────────────
