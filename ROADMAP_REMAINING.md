# StoryForge — état et ensembles restants

Audit du 7 septembre 2026, à partir du document original « Création et gestion des projets » (20 ensembles) et du code local. Les numéros ci-dessous sont ceux du document, pas de nouvelles versions promises.

## Ce qui reste réellement à développer

| Ensemble d’origine | État constaté | Travail restant |
| --- | --- | --- |
| 2 — Création guidée | Quatre guides locaux : démarrage, renforcer une idée, trouver une fin, préparer une scène | Ajouter des guides dédiés personnage, conflit, synopsis et outline ; ajuster la densité du guidage débutant/avancé. |
| 9 — Cartes géographiques | Lieux, images et carte narrative existent, mais pas de carte géographique éditable | Fonds de carte, repères liés aux lieux, terrains, plusieurs échelles et cartes, zoom et déplacement. Chantier précédemment reporté : aucune carte géographique ajoutée dans ce correctif. |
| 18 — Vues d’une histoire | Documents, plan, cartes de scènes, chronologie, relations et scénario partagent les données | Ajouter la vue géographique lorsque l’ensemble 9 sera développé ; renforcer les tests de cohérence entre les vues. |
| 19 — IA contextualisée (optionnelle) | Professeur facultatif, contexte du projet, questions, document de travail et apprentissage | Diagnostics croisés personnages/scènes/timeline/monde ; contrôle du contexte envoyé, retour sourcé dans le projet et propositions toujours soumises à l’auteur. Pas d’IA obligatoire. |
| 20 — Apprentissage connecté | Leçons, progression et accès aux outils présents | Étendre le catalogue et les exercices avec les nouveaux guides ; ce n’est pas un ensemble absent à recommencer. |

Les ensembles 1, 3–8 et 10–17 disposent déjà d’outils correspondants. Cela ne signifie pas que chaque sous-fonction soit exempte de défaut : les évolutions prioritaires sont maintenant des finitions et des tests, pas la réimplémentation de ces ensembles.

## Correctif actuel

- Éditeur : suppression de la surimpression des types ; complétion progressive `IN → INT.`, `E/EX → EXT.` puis lieu et moment ; Action + Entrée → Personnage ; création répétée de scènes typées.
- Vue d’ensemble : scénario affiché avec les retraits des types de paragraphes ; utilisation du document structuré lorsqu’il correspond au texte sauvegardé.
- Export complet : documents lisibles convertis en PDF A4 avec en-tête et pagination. Aucun fichier `.md` dans l’archive ; scénario PDF/FDX, données techniques, images et sauvegarde JSON conservés.
- Navigation : groupe Projets repliable avec état mémorisé ; titres plus espacés ; choix de guide explicite ; taille commune des champs texte.
- Genres : bibliothèque locale de 15 fiches, avec promesse, caractéristiques, distinctions et croisements. Sélectionner un genre ne modifie pas le projet.
- Templates : remplacement des rectangles par des repères sur lignes/courbes ; cercles pour Story Circle et voyage du héros ; carte par actes pour Save the Cat. Les détails restent accessibles au survol.

## À terminer dans la demande actuelle

1. **Anglais intégral** : navigation, boutons courants et certains onglets/libellés sont traduits, avec changement dans Paramètres. Les textes pédagogiques, descriptions longues, certains formulaires, dialogues, options et libellés dynamiques restent à traduire. Les noms et textes de l’utilisateur ne doivent jamais être traduits automatiquement. Le fichier `i18n.py` constitue le catalogue de départ, pas une traduction complète.
2. **Templates illustrés plus spécifiques** : la nouvelle base ne dessine plus de cartes rectangulaires, mais plusieurs structures utilisent encore une courbe de progression générique. Une illustration pédagogique distincte par modèle, proche du niveau de détail de la référence fournie, reste à finaliser.
3. **Contrôle graphique étendu** : les PDF de fiches et quelques écrans ont été contrôlés sur données de test. Tester aussi de très longs projets, les images volumineuses, les petites fenêtres et l’ensemble des écrans dans les deux langues.

## Exporter

- Scénario seul : Éditeur de scripts → Page de garde, puis Exporter PDF ou Exporter FDX.
- Projet complet : Projets → sélectionner le projet → Plus… → Exporter l’histoire terminée… (ou le bouton dans Vue d’ensemble). L’archive ZIP contient les PDF par rubrique et une sauvegarde réimportable ; elle n’oblige pas à déclarer le projet terminé.

Référence visuelle demandée pour les structures : https://writingwithai.com/a-guide-to-the-save-the-cat-beat-sheet-with-chatgpt-brainstorming/ (consultée pour le principe des beats et actes ; illustration non copiée).
