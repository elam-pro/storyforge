# Architecture actuelle

Vérifiée statiquement le 7 septembre 2026 sur le code applicatif 0.30.3. Ce document ne décrit pas une architecture déjà refactorisée.

## Points d’entrée et dépendances

`run_linux.sh` → `app.py:main` → `StoryForgeWindow` → `Database` et modules spécialisés.

| Module | Responsabilité actuelle |
| --- | --- |
| `app.py` | Navigation, vues Qt, état partagé, règles métier, orchestration et SQL direct. |
| `db.py` | Schéma, migrations, requêtes, sauvegarde SQLite, import/export de projet. |
| `screenplay_model.py` | Blocs typés avec identifiants et document sérialisable, indépendant de Qt. |
| `learning_content.py`, `content/sessions/` | Modèles et chargement des guides JSON. |
| `learning_service.py` | Sauvegarde des réponses, progression, fin/réouverture d’étape et miroir historique, sans Qt. |
| `script_export.py` | Parsing, FDX, PDF scénario. |
| `pdf_export.py`, `report_export.py` | Manuel pédagogique et documents PDF. |
| `theme.py`, `i18n.py` | Styles et traduction partielle. |
| `genres.py`, `template_diagrams.py` | Ressources et rendus narratifs. |
| `ai_service.py` | Shim désactivé conservé pour anciens imports ; aucun appel depuis l’interface. |

Le principal couplage reste dans `StoryForgeWindow`. Une première extraction vers `LearningService` sépare la persistance et la progression pédagogique ; les autres domaines restent majoritairement dans la fenêtre.

## Données et écritures

- SQLite locale ; images en BLOB et préférences dans `settings`.
- `Database.__init__` appelle l’initialisation et les migrations. La fenêtre possède aussi des migrations historiques.
- `Database.run` valide les requêtes isolées ; `transaction` protège les opérations composées avec des savepoints imbriqués.
- `Database.import_project` valide format et forme des collections puis remappe les identifiants dans une transaction. Un échec annule les écritures de cet import.
- Certains liens utilisent `target_type/target_id` : vérifier explicitement leur validité et leur appartenance au projet.
- `backup_to` utilise l’API de sauvegarde SQLite. Git ne sauvegarde pas la base personnelle.
- Avant l’ajout de `doc_versions.snapshot_json` à une base existante, le constructeur crée une sauvegarde SQLite dans `backups/`, suffixée `before_structured_versions`. Les bases neuves ne déclenchent pas cette sauvegarde. Pour un retour au code antérieur, restaurer cette copie après fermeture de l’application ; les modifications ultérieures doivent être préservées séparément.

## Scénario : représentations concurrentes

L’éditeur Qt projette `ScreenplayDocument`. Le JSON est dans `script_meta.document_json` et le texte compatible dans `project_docs.content`.
`_save_script` délègue à `Database.save_screenplay` pour sauvegarder atomiquement texte et JSON. `_load_script_document` garde sa compatibilité avec le texte historique. Les nouvelles versions stockent structure et page de garde dans `snapshot_json`, colonne ajoutée sans suppression. Réécriture permet une restauration confirmée avec version de sécurité. Les versions sont également réimportées.
Les anciennes versions textuelles sont reconstruites : leurs types exacts et métadonnées historiques ne sont pas récupérables.

## Apprentissage

Les guides chargés alimentent `guided_runs`, `guided_answers` et `guided_applications`. La maîtrise globale est dans `concept_mastery` ; des tables historiques restent maintenues pour compatibilité.
Une application est unique par parcours/étape. Les méthodes de `StoryForgeWindow` assurent la liaison aux outils et le retour au guide. Ne pas créer un système parallèle sans examiner ces liens.
`LearningService` reçoit la session, le parcours, l’indice et le texte explicitement : aucun widget ni état de fenêtre. Réponses, maîtrise et miroir historique sont sauvegardés ensemble ; terminer une étape inclut la progression dans la même transaction. Les règles existantes sont conservées : acquis reste acquis si la preuve est inchangée, sinon une réponse non vide revient à en pratique. La maîtrise reste globale ; cette extraction ne crée pas de nouvelles preuves par projet.

## Navigation et effets de bord

Les vues sont reconstruites avec des sauvegardes différées et attributs partagés. Les changements de page, timers et caches d’images demandent des tests conjoints.
Terminer le guide initial régénère le manuel dans `output/manuals/`, à côté de la base utilisée. L’export manuel propose aussi ce dossier. L’ancien PDF racine est conservé localement mais ignoré par Git ; son historique Git n’est pas réécrit. Une erreur d’export automatique est signalée sans annuler l’enregistrement du guide.

## Contexte futur

Aucun serveur MCP n’est implémenté. Un futur index devrait lire les sources autorisées, exclure bases/caches/exports/archives par défaut et citer fichier, symbole et révision. Il ne doit pas instancier `Database` pour lire le repository.
Les extractions envisagées sont dans [ROADMAP.md](ROADMAP.md), pas réalisées ici.
