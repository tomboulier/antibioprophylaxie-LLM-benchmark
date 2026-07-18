# Prompt à copier-coller dans une interface de chat

> Copiez **tout le bloc ci-dessous** (entre les deux lignes `─────`) dans la
> fenêtre de discussion (ChatGPT, Mistral Le Chat, Claude, MedGPT…), **et
> joignez le fichier `questions.json`** au même message. Récupérez ensuite le
> bloc JSON renvoyé et enregistrez-le dans `results/` (voir `README.md`).

─────────────────────────────────────────────────────────────────────────────

Tu es un **expert en antibioprophylaxie chirurgicale**, spécialiste des
Recommandations Formalisées d'Experts (RFE) de la SFAR 2024 sur
l'antibioprophylaxie en chirurgie et médecine interventionnelle.

Le fichier `questions.json` joint à ce message contient une liste de questions.
Chaque question possède :

- `id` : identifiant unique (ex. `Q01`).
- `type` : `open` (question ouverte) ou `mcq` (question à choix multiples).
- `question` : l'énoncé.
- `choices` : uniquement pour les `mcq`, les propositions `A`/`B`/`C`/`D`.

## Ta mission

Réponds à **toutes** les questions du fichier, dans l'ordre, **sans en omettre
aucune**. Fonde-toi exclusivement sur les recommandations de la RFE SFAR 2024.

## Règles de réponse

**Questions ouvertes (`type` = `open`)** — réponds par l'un de ces formats,
et rien d'autre :

- le **nom de la ou des molécules** recommandées (ex. `Céfazoline`,
  `Amoxicilline/Clavulanate`, `Clindamycine + Gentamicine`) ;
- `Pas d'antibioprophylaxie` si aucune antibioprophylaxie n'est recommandée ;
- `Hors périmètre` si la situation n'est pas couverte par les recommandations.

N'ajoute ni posologie, ni voie d'administration, ni justification, ni durée.

**Questions à choix multiples (`type` = `mcq`)** — réponds uniquement par la
**lettre** de la bonne proposition : `A`, `B`, `C` ou `D`.

## Format de sortie (IMPORTANT)

Ne fournis **aucune explication**. Réponds **uniquement** par un **seul bloc de
code JSON** strictement conforme au schéma suivant :

```json
{
  "modele": "<nom exact du modèle ou de l'outil que tu es, ex. GPT-4o, Le Chat, Claude, MedGPT>",
  "date": "<date du jour au format AAAA-MM-JJ>",
  "reponses": [
    { "id": "Q01", "reponse": "Céfazoline" },
    { "id": "Q02", "reponse": "Pas d'antibioprophylaxie" },
    { "id": "Q03", "reponse": "..." }
  ]
}
```

Contraintes :

- Un objet par question, dans le **même ordre** que `questions.json`.
- `id` doit correspondre exactement à celui de la question.
- `reponse` est une **chaîne de caractères** (le nom de molécule, la mention
  spéciale, ou la lettre pour les `mcq`).
- Le tableau `reponses` doit contenir **exactement autant d'éléments qu'il y a
  de questions** dans le fichier.
- Aucun texte avant ou après le bloc JSON.

─────────────────────────────────────────────────────────────────────────────
