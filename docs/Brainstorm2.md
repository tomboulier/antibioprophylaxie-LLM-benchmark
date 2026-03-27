Brainstorm 2 : Format du benchmark (Starbursting)
  
  Les questions clés à trancher :

  QUI ?
  - Qui rédige les questions ? Toi seul pour le POC, experts ensuite ? oui c'est ça, je commence à faire un jeu de questions "faciles" avec les recos d'antibio, et du coup ça montre et motive les gens à aller plus loin
  - Qui valide les réponses attendues ? les experts (comité des référentiels, GIHP, etc.)
  - Qui est le "consommateur" du dataset (dev ? médecin ? reviewer de journal ?) ça peut être les dev qui font un nouvel pour voir ses performances, un médecin qui pourrait se former sur les RFEs (cas d'usage pas prévu au début, mais bel effet de bord pédagogique je trouve)
                                                                                                                                                    
  QUOI ?
  - Quels types de questions ? (factuel direct, QCM, vignette clinique, cas piège) QCM parce que ça me semble être le plus simple ; factuel direct pour commencer oui ; vignette clinique à terme, avec des QCM, idem c'est simple pour faire de la vérification déterministre ; cas piège clairement (cf. métadonnées de questions)
  - Quelles métadonnées par question ? (difficulty, specialty, RFE_section, scoring_rubric) : attention à ne pas trop en mettre (KISS/YAGNI+++) ! pour le moment, difficulté je suis d'accord, type de question pourquoi, mais pour le moment on ne s'embarasse pas trop pour la V1
  - Quel format de réponse attendue ? (texte libre, liste de mots-clés, rubric multi-critères) => pour les QCM ça doit juste répondre par une lettre, mais on peut aussi demander de répondre juste par un nom de molécule, juste une posologie, etc. une fois de plus, LLM-as-a-judge je suis pas fan pour le moment, donc on commence par un truc simplissime 
                                                                                                                                                    
  COMMENT ?
  - Comment publier le dataset ? (JSON dans le repo + HuggingFace + data paper ?) oui tout ça c'est très bien
  - Comment versionner ? (le dataset évolue quand la RFE change) avec des numéros de version (j'imagine qu'il y a une sorte de semantic versioning pour les données) ; et il me semble que zenodo permet de fournir des doi pour y faire référence
  - Comment le rendre multilingue à terme ? (anglais pour ICM/ESICM) : pour les RFEs SFAR je suis pas sûr que ça soit une bonne idée de penser au multilingue ; pour ICM/ESICM on verra en tant voulu, mais en gros ça dépendra de la langue des recommandations tout simplement (cf. le dataset suédois)
                                                                                                                                                    
  POURQUOI certains choix plutôt que d'autres ?
  - Pourquoi pas uniquement des QCM ? (plus facile à scorer, mais moins réaliste)
  - Pourquoi pas uniquement des vignettes ? (plus réaliste, mais plus dur à scorer de manière déterministe)
  => tu réponds tout seul à ces questions c'est bien :) disons du coup pour commencer plutôt QCM parce que c'est simple (KISS), et on verra après si on veut/peut complexifier (YAGNI)
  - Pourquoi du JSON et pas un format standard type SQuAD ou MMLU ? je connais pas SQuAD ou MMLU, c'est quoi ?
                                                                                                                                                    
  ET SI ?
  - Et si un LLM a vu les RFEs SFAR en entraînement ? → les vignettes cliniques discriminent mieux que les questions factuelles directes => bah c'est très bien, on verra justement s'ils sont meilleurs ! et si besoin de RAG, ou juste attendre que les LLMs aient les RFEs dans leur entraînement (c'est comme si c'était du fine-tuning quoi). les vignettes cliniques je pense surtout que ça permettra une forme de "raisonnement", mais bon questions factuelles pour une V1 c'est bien une fois de plus
  - Et si les experts ne sont pas d'accord sur la bonne réponse ? → scoring pondéré, kappa inter-rater => oui d'accord (j'avais le kappa en tête, je ne sais pas ce qu'est le scoring pondéré)
  - Et si le dataset devient un standard adopté par d'autres ? → il faut un format extensible dès le départ => dans quel sens ?
