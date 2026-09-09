# Architecture actuelle

Vérifiée le 9 septembre 2026 sur le code applicatif 0.31.0.

## Points d’entrée et dépendances

Installation : `install_linux.sh` → PyInstaller → `dist/StoryForge` →
`~/.local/lib/storyforge/StoryForge`. Développement : `run_linux.sh` →
`python -m storyforge` → `storyforge.app:main` → `StoryForgeWindow` →
`Database` et modules spécialisés.

| Module | Responsabilité actuelle |
| --- | --- |
| `storyforge/app.py` | Navigation, vues Qt, état partagé, règles métier, orchestration et SQL direct. |
| `storyforge/db.py` | Schéma, migrations, requêtes, sauvegarde SQLite, import/export de projet. |
| `storyforge/runtime_paths.py` | Emplacements XDG et copie atomique contrôlée de l’ancienne base. |
| `storyforge/screenplay_model.py` | Blocs typés avec identifiants et document sérialisable, indépendant de Qt. |
| `storyforge/screenplay_adapter.py` | Lecture des paragraphes Qt et résolution texte/JSON, sans fenêtre ni accès à la base. |
| `storyforge/learning_content.py`, `storyforge/content/sessions/` | Modèles et chargement des guides JSON. |
| `storyforge/learning_service.py` | Réponses, progression, miroir historique, applications aux outils et changements de maîtrise, sans Qt. |
| `storyforge/script_export.py` | Parsing, FDX, PDF scénario. |
| `storyforge/pdf_export.py`, `storyforge/report_export.py` | Manuel pédagogique et documents PDF. |
| `storyforge/theme.py`, `storyforge/i18n.py` | Styles et traduction partielle. |
| `storyforge/genres.py`, `storyforge/template_diagrams.py` | Ressources et rendus narratifs. |
| `storyforge/geography.py` | Canevas Qt des cartes, repères déplaçables, panoramique et zoom ; la persistance reste orchestrée par la fenêtre. |
| `storyforge/ai_service.py` | Shim désactivé conservé pour anciens imports ; aucun appel depuis l’interface. |

Le principal couplage reste dans `StoryForgeWindow`. Une première extraction vers `LearningService` sépare la persistance et la progression pédagogique ; les autres domaines restent majoritairement dans la fenêtre.

## Données et écritures

- SQLite locale ; images en BLOB et préférences dans `settings`.
- En installation normale, la base et ses sauvegardes sont sous
  `~/.local/share/storyforge/`, la configuration sous `~/.config/storyforge/`, le
  cache sous `~/.cache/storyforge/` et les exports sous `~/Documents/StoryForge/`.
- `STORYFORGE_DB_PATH`, `STORYFORGE_DATA_DIR` et `STORYFORGE_EXPORT_DIR`
  permettent des emplacements explicites pour les tests et outils. Une ancienne
  base du dépôt est copiée sans écrasement via l’API de sauvegarde SQLite puis
  contrôlée avec `PRAGMA integrity_check`.
- `Database.__init__` appelle l’initialisation et les migrations. La fenêtre possède aussi des migrations historiques.
- `Database.run` valide les requêtes isolées ; `transaction` protège les opérations composées avec des savepoints imbriqués.
- `Database.import_project` valide format et forme des collections puis remappe les identifiants dans une transaction. Un échec annule les écritures de cet import.
- Certains liens utilisent `target_type/target_id` : vérifier explicitement leur validité et leur appartenance au projet.
- `backup_to` utilise l’API de sauvegarde SQLite. Git ne sauvegarde pas la base personnelle.
- Avant l’ajout de `doc_versions.snapshot_json` à une base existante, le constructeur crée une sauvegarde SQLite dans `backups/`, suffixée `before_structured_versions`. Les bases neuves ne déclenchent pas cette sauvegarde. Pour un retour au code antérieur, restaurer cette copie après fermeture de l’application ; les modifications ultérieures doivent être préservées séparément.
- Avant l’ajout des tables géographiques à une base existante comportant déjà les lieux, le constructeur crée de même une copie `backups/*before_geography_maps*.db`. `geography_maps` référence éventuellement une image existante ; `geography_markers` référence éventuellement un lieu existant. L’export de projet remappe ces deux références au réimport. Supprimer une carte cascade seulement vers ses repères, jamais vers les lieux ou images sources.

## Scénario : représentations concurrentes

L’éditeur Qt projette `ScreenplayDocument`. Le JSON est dans `script_meta.document_json` et le texte compatible dans `project_docs.content`.
`screenplay_adapter.block_values` lit les paragraphes en une passe ; `block_type` conserve les états Qt explicites et infère les anciens paragraphes sans récursion. `load_document` refuse les structures invalides/futures et conserve la priorité historique du texte en cas de désaccord avec un JSON valide. `screenplay_commands` isole les règles de transition et les dimensions des retraits ; leur application Qt et l’orchestration des exports restent dans la fenêtre.
`_save_script` délègue à `Database.save_screenplay` pour sauvegarder atomiquement texte et JSON. `_load_script_document` garde sa compatibilité avec le texte historique. Les nouvelles versions stockent structure et page de garde dans `snapshot_json`, colonne ajoutée sans suppression. Réécriture permet une restauration confirmée avec version de sécurité. Les versions sont également réimportées.
Les anciennes versions textuelles sont reconstruites : leurs types exacts et métadonnées historiques ne sont pas récupérables.

## Apprentissage

Les guides chargés alimentent `guided_runs`, `guided_answers`, `guided_applications` et `guided_application_history`. La maîtrise globale est dans `concept_mastery` ; des tables historiques restent maintenues pour compatibilité.
`guided_applications` conserve l’état courant unique par parcours/étape. Chaque ouverture d’un outil ou changement explicite de maîtrise ajoute aussi une trace contextuelle dans `guided_application_history` ; une nouvelle application ne détruit donc plus les précédentes. `LearningService.apply_to_tool` enregistre preuve, historique, maîtrise et contexte de retour dans une transaction. `set_mastery` exige une application pour marquer acquis et synchronise réponse, preuve et état. `StoryForgeWindow` conserve le choix des cibles, les messages et la navigation effective. Ne pas créer un système parallèle sans examiner ces liens.
`LearningService` reçoit la session, le parcours, l’indice et le texte explicitement : aucun widget ni état de fenêtre. Réponses, maîtrise et miroir historique sont sauvegardés ensemble ; terminer une étape inclut la progression dans la même transaction. Les règles existantes sont conservées : acquis reste acquis si la preuve est inchangée, sinon une réponse non vide revient à en pratique. La maîtrise reste globale, tandis que les preuves sont contextualisées par parcours, projet, cible et champ.

L’ajout de l’historique est une migration additive : une base existante reçoit une sauvegarde restaurable `backups/*before_connected_learning_history*.db` avant création et ses applications courantes sont reprises comme traces `legacy`. Revenir à un code antérieur impose de fermer l’application puis de restaurer cette copie si l’on veut retrouver exactement le schéma précédent.

## Géographie connectée

L’onglet `Univers > Cartes` est une représentation supplémentaire des mêmes données, pas une bibliothèque parallèle. Une carte porte son nom, son indication d’échelle, ses dimensions de canevas et éventuellement l’identifiant d’une image de fond. Un repère lié conserve l’identifiant du lieu ; son libellé cartographique, ses notes et sa position restent propres à la carte. Un repère libre décrit un terrain, une frontière, une route ou un autre élément qui ne justifie pas encore une fiche Lieu. `GeographyView` gère uniquement l’affichage et les gestes ; `StoryForgeWindow` valide le projet et écrit en base.
`render_geography_map` produit une image bornée indépendante de la vue affichée. L’export final l’utilise pour livrer un PNG par carte, un index PDF et un CSV des repères ; la sauvegarde JSON demeure la source réimportable.

## Navigation et effets de bord

Les vues sont reconstruites avec des sauvegardes différées et attributs partagés. Les changements de page, timers et caches d’images demandent des tests conjoints.
Terminer le guide initial régénère le manuel dans `~/Documents/StoryForge/Manuels`
pour l’installation normale. Avec une base temporaire explicitement fournie, le
manuel reste à côté de cette base afin d’isoler les tests. Une erreur d’export
automatique est signalée sans annuler l’enregistrement du guide.

## Distribution Linux

`scripts/build_linux.sh` produit un exécutable monofichier PyInstaller et y
embarque les guides et ressources visuelles. `packaging/linux/install_application.py`
installe cet exécutable, le fichier `.desktop`, l’icône et la commande utilisateur
par copies atomiques. `uninstall_linux.sh` ne retire que ces éléments installés :
les données sont intentionnellement conservées. `tools/organize_workspace.py`
déplace les anciens fichiers runtime hors du dépôt après copie et vérification ;
il conserve les environnements de développement. `scripts/package_linux_release.sh`
produit une archive versionnée autonome : elle inclut l’exécutable, les installateurs,
l’icône, les composants minimaux de migration et un inventaire SHA-256. Son script
d’installation n’exige ni checkout Git, ni PySide6, ni reconstruction.

## Index de contexte du repository

`storyforge_context.index.RepositoryIndex` utilise une liste explicite de sources,
croisée avec les fichiers suivis par Git. Il lit uniquement les fichiers courants,
pas les anciens blobs Git. Les empreintes sont recalculées à chaque requête ;
seuls les contenus modifiés sont reparsés. Index en mémoire, sans SQLite ni import
du runtime applicatif. Python est découpé par AST (sans exécution), Markdown par
sections/lignes de tableau ; les douze JSON pédagogiques sont autorisés nommément,
pas par motif générique. `FEATURES.md` relie domaine, symboles et tests.

Provenance : révision HEAD, blob de l’index Git, SHA-256 du contenu effectivement
lu, modifications indexées/non indexées, fichier, symbole et lignes. Lecture par
descripteurs avec refus des liens symboliques, liens physiques et fichiers
spéciaux. Bases, fichiers privés, archives, exports et sources non suivies sont
hors liste. Certains formats de secrets évidents sont refusés ; aucun filtre
heuristique ne garantit qu’un secret copié dans du code autorisé sera reconnu.
Ne jamais inclure de données utilisateur dans ces sources ou tests.

Sorties bornées à 12 000 caractères JSON, huit extraits maximum pour une recherche,
1 800 caractères par extrait. Une source devenue invalide est retirée plutôt que
servie périmée. Les extraits sont des données non fiables, pas des instructions.
`tests/test_context_index.py` vérifie les limites et exclusions sur dépôts temporaires.

`storyforge_context.server.create_server` enveloppe cet index dans le SDK MCP
optionnel, uniquement via STDIO. Sept outils annotés lecture seule et cinq
ressources canoniques ; aucun outil d’exécution, d’écriture ou de lecture d’histoire.
Configuration et validation de protocole : [MCP.md](MCP.md).
