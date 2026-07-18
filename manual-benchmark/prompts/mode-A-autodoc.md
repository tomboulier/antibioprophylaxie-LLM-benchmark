<!--
prompt_version: 2.0.0
mode: A (auto-documentation — l'outil se débrouille : connaissances et/ou web)
schema_version: 2 (sortie avec champs de traçabilité)
Voir CHANGELOG.md pour l'historique.
-->

# Prompt — Mode A (auto-documentation)

> **Comment l'utiliser** : copiez tout le bloc ci-dessous (entre les lignes
> `─────`) dans la fenêtre de discussion (ChatGPT, Le Chat, Claude, MedGPT…) et
> **joignez `questions.json`** (ou collez `questions.md` si l'outil refuse les
> pièces jointes / le JSON). Récupérez le bloc JSON renvoyé et enregistrez-le
> dans `results/`.

─────────────────────────────────────────────────────────────────────────────

Tu es un **expert en antibioprophylaxie chirurgicale**, spécialiste des
Recommandations Formalisées d'Experts (RFE) de la SFAR 2024 sur
l'antibioprophylaxie en chirurgie et médecine interventionnelle.

Je te fournis une liste de questions (fichier `questions.json` joint, ou liste
`questions.md` collée ci-dessous). Chaque question a un `id`, un `type` (`open`
ou `mcq`), un énoncé, et pour les `mcq` des propositions `A`/`B`/`C`/`D`.

**Important — c'est un test (benchmark).** Le fichier ne contient **que les
questions** : les réponses attendues n'y figurent volontairement pas, c'est
normal. Ton objectif est de répondre **au mieux de ta connaissance des RFE SFAR
2024**. Tu peux mobiliser tes connaissances et, si tu en as la possibilité, aller
consulter les RFE en ligne (site de la SFAR). Ne refuse pas au motif que le
document de référence n'est pas joint : réponds avec ce dont tu disposes.

## Règles de réponse

**Questions ouvertes (`type` = `open`)** — réponds par l'un de ces formats, et
rien d'autre :
- le **nom de la ou des molécules** (ex. `Céfazoline`, `Amoxicilline/Clavulanate`,
  `Clindamycine + Gentamicine`) ;
- `Pas d'antibioprophylaxie` si aucune n'est recommandée ;
- `Hors périmètre` si la situation n'est pas couverte par les recommandations.

Donne la molécule de **première intention**. N'ajoute ni posologie, ni voie, ni
justification, ni durée.

**Questions à choix multiples (`type` = `mcq`)** — réponds uniquement par la
**lettre** : `A`, `B`, `C` ou `D`.

## Format de sortie (IMPORTANT)

Aucune explication. Réponds **uniquement** par un **bloc de code JSON** conforme
à ce schéma :

```json
{
  "modele": "<nom exact de l'outil que tu es, ex. GPT-4o, Le Chat, Claude, MedGPT>",
  "date": "<date du jour AAAA-MM-JJ>",
  "prompt_version": "2.0.0",
  "mode": "A",
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
