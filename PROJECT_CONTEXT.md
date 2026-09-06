# StoryForge — contexte de continuité Codex

Dernière mise à jour : 2026-09-06

Ce fichier est la mémoire opérationnelle du projet. Il complète l’historique des conversations Work/Codex sans le remplacer. Il doit être mis à jour lorsqu’une décision importante, une version ou une prochaine étape change.

## 1. Identité du projet

- Nom : StoryForge Desktop
- Objectif : application locale pour apprendre à imaginer, construire, écrire, analyser et réécrire des histoires cinématographiques.
- Plateforme : Linux uniquement.
- Dossier de travail unique : `/home/elam/Documents/Test/storyforge_desktop_v051`
- Interface : PySide6, application locale, sans IA obligatoire, sans abonnement et sans synchronisation distante.
- Base de données locale : SQLite (`storyforge.db`, ignorée par Git car elle contient les données de travail).
- Version déclarée dans `app.py` : `0.29.0`.
- `README.md` et `RELEASE_NOTES.md` suivent désormais la version visible courante `0.29.0`.

## 2. Règles de travail à respecter

1. Travailler dans le dossier existant. Ne pas créer un nouveau dossier projet.
2. Ne pas ajouter de dépendance payante, de clé API ou de service IA obligatoire.
3. Ne pas viser Windows : le périmètre est Linux.
4. Préserver les données existantes et les migrations SQLite.
5. Avant une modification importante : vérifier `git status`, faire une sauvegarde si nécessaire, puis tester.
6. Après une modification cohérente : mettre à jour la documentation concernée et créer un commit Git clair.
7. Ne pas supprimer une ancienne fonctionnalité sans migration, sauvegarde ou demande explicite.
8. Pour l’interface, privilégier une esthétique Studio sobre : panneaux denses, angles cohérents, accent rouge-orangé, peu d’effets décoratifs et pas d’apparence « tableau de bord IA ».
9. Les structures narratives sont des outils facultatifs. Aucune structure en trois actes ne doit être imposée.
10. L’application doit guider l’écriture sans remplacer l’auteur : une question ciblée, un exemple, un essai, un feedback puis une réécriture.

## 3. État Git et sauvegardes

- Branche actuelle : `main`
- Commit de base avant migration : `74cc3ba chore: baseline StoryForge before Codex migration`
- Dernier commit connu : `c8b3fb8 feat: make screenplay editor structure visible`
- Tags de sécurité :
  - `v0.27.1-before-codex`
  - `v0.27.1-before-codex-tested`
  - `v0.28.0-before-screenplay`
  - `v0.28.0-stabilisation-tested`
  - `v0.28.1-screenplay-tested`
  - `v0.29.0-screenplay-visual`
- Remote Git : `origin git@github.com:elam-pro/storyforge.git`.
- Le dernier état contrôlé était propre : `git status --short --branch` affichait `## main`.
- Archive complète pré-Codex : `/home/elam/Documents/Test/storyforge_desktop_v051_pre_codex_2026-09-06.tar.gz`
- Sauvegarde SQLite : `/home/elam/Documents/Test/storyforge_desktop_v051/backups/storyforge_pre_codex_2026-09-06.db`
- Les anciennes versions et archives hors `v051` ont été déplacées dans la corbeille Linux ; elles restent récupérables.

## 4. Commandes utiles

Depuis la racine du projet :

```bash
./run_linux.sh
```

Installation ou réparation de l’environnement :

```bash
./install_linux.sh
```

Tests complets :

```bash
.venv/bin/python -m pytest -q
```

La dernière vérification connue après la V0.29.0 était : `54 passed`.

Contrôles Git recommandés :

```bash
git status --short --branch
git log --oneline --decorate -8
```

## 5. Architecture utile

- `app.py` : fenêtre principale, navigation, vues et interactions PySide6.
- `db.py` : schéma SQLite, accès aux données et migrations locales.
- `theme.py` : tokens et styles de l’interface.
- `script_export.py` : lecture/écriture FDX, PDF scénario et parsing du script.
- `pdf_export.py` : export du manuel pédagogique.
- `learning_content.py` : contenus des guides et sessions.
- `ai_service.py` : couche optionnelle ; ne jamais en faire une dépendance obligatoire.
- `content/sessions/` : contenus pédagogiques JSON.
- `tests/` : tests unitaires, d’intégration et smoke tests.

## 6. Fonctionnalités validées par version

### V0.29.0 — état actuel

- Le canevas de l’Éditeur de scripts affiche un rail de type non éditable à gauche de chaque paragraphe.
- La ligne active est surlignée et les six formats sont plus lisibles dans la barre d’outils.
- La structure `ScreenplayDocument`, les IDs persistants et la migration `script_meta.document_json` restent inchangés.

### V0.28.1 — fondation de l’éditeur structuré

- `screenplay_model.py` fournit un modèle indépendant du `QTextEdit`, avec types de blocs, IDs persistants et sérialisation JSON.
- Les scénarios historiques sont migrés automatiquement sans supprimer le texte compatible de `project_docs.content`.
- `script_meta.document_json` conserve la représentation structurée et reste exportable/réimportable.
- L’éditeur existant, ses raccourcis et sa navigation sont conservés.

### V0.28.0 — stabilisation

- Les entrées du panneau latéral gardent une hauteur réservée identique pour éviter les chevauchements.
- Les changements rapides de projet sont regroupés avant de reconstruire l’espace de travail.
- Les aperçus des lieux se chargent après l’affichage du panneau et les aperçus obsolètes sont ignorés.
- Pour la V0.28 publiée, le schéma SQLite et les formats d’export restent inchangés.

### V0.27.1 — migration Codex

- Correctif de chargement initial des connexions de personnages.
- Base Git migrée et testée.
- Les fonctions de la V0.26 restent disponibles.

### V0.26 — Vue d’ensemble et export final

- Vue d’ensemble coordonnée : Documents, Plan, Cartes, Chronologie, Relations et Script.
- Filtres communs et ouverture directe de l’outil source.
- Export final volontaire dans une archive unique.
- Script en PDF, FDX et Fountain.
- Chronologie en Markdown et CSV.
- Fiches Personnages, relations, lieux, univers, règles, thème, conflits, promesses et images.
- Sauvegarde StoryForge complète et réimportable incluse dans l’archive.

### V0.25 — Recherche et tags

- Recherche globale avec `Ctrl+K`.
- Tags communs au projet et filtres par tag.
- Conservation des tags dans les exports/imports.

### V0.24 — Modèles de fiches

- Modèles de fiches séparés des templates de structure.
- Champs courts/longs, nombres, dates, listes, tags, cases, images et liens internes.
- Modèles assignables par projet et par type de fiche.

### V0.23 — Éditeur de scripts professionnel

- Six formats : scène, action, personnage, dialogue, parenthèse et transition.
- Tab/Maj+Tab intelligents, sans création de texte vide artificiel.
- Retour arrière progressif vers l’élément précédent.
- `(CONT'D)` sur un dialogue consécutif du même personnage.
- Contexte de scène repliable, mode Concentration, versions, import/export FDX et export PDF.
- Page de titre, numérotation et mise en page scénario prises en charge par l’export.

### V0.22 — Scènes connectées et interface harmonisée

- Scènes structurées en Noyau, Déroulement et Connexions.
- Objectif, obstacle, information, changement, entrée, sortie, durée et statut.
- Trois niveaux d’action visuelle : principale, secondaire, tertiaire/suppression.
- Boutons Annuler cohérents dans Personnages et Lieux.

### V0.18 à V0.21 — Thème, conflits, arcs, promesses et Studio

- Thème et motifs facultatifs.
- Conflits connectés.
- Interface Studio sombre, panneau latéral repliable/dépliable.
- Arcs et transformations.
- Accroche et promesses.

### V0.14 à V0.16 — Relations, chronologie, personnages, univers et lieux

- Carte de relations directionnelle avec nœuds, groupes, filtres et cartes multiples.
- Chronologies multiples, libres dans les deux axes, événements éditables au double-clic.
- Personnages avec rôles structurés, groupes, moodboard, silhouettes Femme/Homme et connexions.
- Univers en quatre onglets : Cadre, Règles, Histoire, Lexique.
- Lieux connectés aux personnages, événements, scènes et images.

### V0.8 à V0.13 — Fondations narratives

- Banque d’idées avec catégories, filtres, images et variantes « Et si ? ».
- Graine → Projet → Construction.
- Construction : prémisse, logline, synopsis guidé, treatment, carte de beats, séquencier et liste de scènes.
- Guides d’écriture et Guides en cours dans la barre latérale.
- Bibliothèque de templates, Glossaire et bibliothèque d’images.

## 7. Organisation pédagogique du projet

Le parcours de référence est :

`Idées → Noyau dramatique → Personnages/Conflit → Carte de l’histoire → Synopsis/Treatment → Beats/Outline/Séquencier → Scènes → Premier jet → Feedback → Réécritures`

Les documents servent à tester des hypothèses à différents niveaux de détail ; ils ne sont pas des formulaires de validation obligatoires.

Repères de vocabulaire :

- **Séquence** : groupe de scènes qui produit un mouvement narratif identifiable.
- **Beat** : changement court dans une scène ou une séquence : décision, information, renversement ou réaction.
- **Scène** : unité située dans un lieu et un moment, avec une action et un changement.
- **Séquencier/outline** : ordre de travail des séquences ou scènes avant l’écriture complète.

## 8. Décisions d’interface déjà validées

- Une colonne de navigation peut être repliée en icônes ou dépliée avec les textes.
- Les intitulés du panneau latéral doivent rester lisibles et alignés.
- Personnages et Lieux suivent une logique de blocs comparable : bibliothèque, image/références, fiche.
- Les cadres doivent être cohérents : même géométrie, mêmes niveaux de boutons et tailles de police harmonisées.
- Les champs éditables doivent être clairement bordés et réellement cliquables.
- Les canevas Carte de l’histoire, Relations et Chronologie se déplacent avec le curseur.
- Les listes importantes doivent rester utilisables avec beaucoup d’éléments : recherche, filtres et défilement.
- Le sélecteur de projet actif doit être disponible dans les espaces concernés.

## 9. Points à vérifier avant le prochain chantier

Ces points sont des contrôles prioritaires, pas nécessairement des bugs confirmés :

1. Vérifier visuellement l’export PDF scénario sur plusieurs pages et avec page de titre.
2. Vérifier l’import/export FDX sans perte de types de paragraphes ni de dialogues `(CONT'D)`.
3. Vérifier l’export final complet puis sa réimportation dans une copie de test.
4. Vérifier les performances quand un projet contient beaucoup de personnages, lieux ou images.
5. Vérifier que les onglets internes restent lisibles après changement de taille de fenêtre.
6. Conserver la refonte graphique générale en attente tant qu’un nouveau style n’est pas explicitement choisi.

## 10. Prochaine étape

Avant toute nouvelle fonctionnalité, demander ou confirmer l’ensemble/version à traiter, puis :

1. lire ce fichier et `README.md` ;
2. vérifier `git status` ;
3. reproduire le problème ou écrire un test ;
4. modifier le minimum nécessaire ;
5. lancer les tests complets ;
6. faire un commit décrivant le changement ;
7. mettre à jour ce fichier si la roadmap ou une décision change.

Prompt de reprise recommandé dans Codex :

```text
Lis PROJECT_CONTEXT.md et README.md.
Vérifie git status et le dernier commit.
Reprends le travail à la section « Points à vérifier avant le prochain chantier »
ou à l’ensemble que je vais préciser. Travaille dans le dossier existant,
préserve les données SQLite et lance les tests avant de conclure.
```
