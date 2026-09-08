# État des fonctionnalités

État mis à jour le 9 septembre 2026, code 0.30.3. « Présent » signifie qu’un chemin de code existe, pas absence de défaut. Tests ci-dessous = points de contrôle existants, pas preuve de couverture exhaustive.

| ID / domaine | État et limite | Code à chercher | Tests existants |
| --- | --- | --- | --- |
| learning.guides | Présent : sept guides locaux, dont Personnage, Conflit et Synopsis, facultatifs avec relecture et reprise. Catalogue limité. | `learning_content.py`, `content/sessions/`, `app.py:show_learning` | `tests/test_learning_content.py`, `tests/test_character_guide.py`, `tests/test_conflict_guide.py`, `tests/test_synopsis_guide.py`, `tests/test_ui_smoke.py` |
| learning.application | Partiel : outils et cibles reliés, maîtrise déclarée ; une application par étape et maîtrise globale. | `app.py:_learning_tool_link`, `_save_learning_work`, `db.py:save_guided_application` | `tests/test_v027_connected_learning.py`, `tests/test_database.py` |
| projects | Présent : création, états, archivage, import/export ; import transactionnel avec validation de forme. | `db.py:import_project`, `export_project`, `app.py` | `tests/test_database.py`, `tests/test_ui_smoke.py` |
| ideas | Présent : catégories, images, variantes Et si. | `app.py:show_ideas`, `db.py` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| construction | Présent : documents, cartes, outline, séquences et scènes connectées. | `app.py:show_development`, `_build_scene_list_workspace`, `db.py` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| characters.relations | Présent : fiches, groupes, portraits, références et cartes directionnelles. | `app.py:show_characters`, `RelationshipMapDialog` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| world.locations | Présent : cadre, règles, lexique et lieux connectés ; pas de carte géographique éditable. | `app.py:show_locations`, `db.py` | `tests/test_database.py`, `tests/test_ui_smoke.py` |
| timeline | Présent : pistes et événements, connexions et canevas. Charge importante à tester. | `app.py:TimelineView`, `_timeline_event_dialog` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| narrative.analysis | Présent : arcs, conflits, thèmes, motifs et promesses ; pas d’évaluation IA opérationnelle. | `app.py`, tables associées dans `db.py` | `tests/test_database.py`, `tests/test_v026_overview_export.py` |
| screenplay.editor | Partiel : blocs typés, IDs, raccourcis, complétion et aperçu. Sauvegarde atomique ; nouvelles versions structurées et restauration confirmée. Versions anciennes reconstruites. | `screenplay_model.py`, `app.py:ScreenplayEditor`, `_load_script_document`, `_save_script`, `_snapshot_script` | `tests/test_screenplay_model.py`, `tests/test_screenplay_persistence.py`, `tests/test_editor_polish.py`, `tests/test_layout_followup.py` |
| screenplay.exchange | Partiel : PDF paginé/page de garde, Unicode selon les polices installées ; FDX des six types éditables. Pas de FDX sans perte de styles/révisions. | `script_export.py`, `unicode_script_pdf.py` | `tests/test_script_export.py`, `tests/test_screenplay_consolidation.py` |
| project.export | Présent : ZIP, PDF de rubriques, scénario et données réimportables ; ne remplace pas toute la base. | `app.py:_build_final_story_export`, `db.py:export_project`, `report_export.py` | `tests/test_report_export.py`, `tests/test_v026_overview_export.py` |
| resources | Présent : genres, glossaire, templates et modèles de fiches. Schémas parfois génériques. | `genres.py`, `template_diagrams.py`, `app.py:show_form_templates` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| templates.images | Présent : personnalisation globale en settings ; absente de l’export individuel de projet. | `app.py` : chercher `template_image_` | `tests/test_layout_followup.py` |
| search.navigation | Présent : recherche, tags, vues coordonnées et menu Projets repliable. | `app.py:show_search`, `show_story_overview`, `_build_shell` | `tests/test_ui_smoke.py`, `tests/test_layout_followup.py` |
| language | Partiel : libellés anglais, contenus longs et formulaires encore incomplets. | `i18n.py`, appels `tr` dans `app.py` | `tests/test_editor_polish.py` |
| ai.professor | Désactivé : `ask` lève une erreur ; shim et données conservés, ancienne interface et worker retirés. | `ai_service.py:ProfessorAI`, tables historiques dans `db.py` | `tests/test_cleanup.py` vérifie la conservation des données ; service indisponible. |
| geography | Prévu, non implémenté. | Aucun outil géographique dédié identifié. | Pas de garantie existante. |
| repository.mcp | Présent : sept outils et cinq ressources de contexte du repository, STDIO en lecture seule ; SDK optionnel et connexion à recharger côté client. Aucune histoire personnelle. | `storyforge_context/server.py:create_server`, `run_context_mcp.sh` | `tests/test_mcp_server.py` ; [installation et limites](MCP.md) |
| repository.index | Présent : sources autorisées suivies par Git, index incrémental en mémoire, recherche lexicale et liens fonctionnalités/code/tests ; aucune histoire personnelle. | `storyforge_context/index.py:RepositoryIndex` | `tests/test_context_index.py` |

## Garanties et limites de validation

Les caches d’aperçus personnages/lieux sont bornés via `image_previews.py`.
Mesures reproductibles et limites : [PERFORMANCE.md](PERFORMANCE.md).

`screenplay_adapter.py` sépare la projection Qt et le chargement compatible. Le JSON invalide, les types inconnus, les IDs dupliqués et les versions futures sont refusés sans remplacement par le texte. `screenplay_commands.py` isole transitions et retraits. L’import FDX structuré conserve les six types éditables, y compris les paragraphes vides ; styles, révisions et extensions Final Draft ne sont pas garantis. Le PDF Unicode utilise les polices incorporées de Qt, le chemin WinAnsi historique reste conservé. Les alphabets disponibles dépendent des polices installées ; pas de garantie universelle pour tous les glyphes. `tests/test_screenplay_consolidation.py` et `tests/test_screenplay_adapter.py` couvrent ces frontières, les IDs et 2 000 paragraphes. Rendu contrôlé sur couverture, réplique longue, MORE/CONT'D et caractères vietnamiens, polonais et cyrilliques.

La sauvegarde, la progression, les applications et les changements explicites de maîtrise passent par `learning_service.py:LearningService`. `tests/test_learning_service.py` vérifie sans Qt les miroirs historiques, la maîtrise, la fin/réouverture, l’isolation des réponses, les preuves et l’annulation sur erreur. La sélection des cibles et la navigation restent dans l’interface ; `tests/test_v027_connected_learning.py` protège leur intégration.

Le guide **Construire un personnage**, dans Guides d’écriture puis Guides en cours, propose situation initiale, objectif, motivation, contradiction, épreuve révélatrice et évolution facultative. L’idée de scène va dans les notes, sans créer de scène.

Le guide **Construire un conflit** explore les volontés ou forces en présence, l’incompatibilité, les enjeux, la pression, les choix et une issue provisoire. Il accepte une opposition extérieure, intérieure ou matérielle sans imposer antagoniste, escalade ni résolution. Ses sept réponses ciblent les champs existants `side_a_goal`, `side_b_goal`, `incompatibility`, `stakes`, `escalation`, `difficult_choice` et `outcome`. L’ouverture de l’outil sélectionne la fiche et l’onglet Noyau ou Progression, avec retour au guide.

Le guide **Construire un synopsis** ne crée pas un second outil parallèle. Ses six étapes correspondent exactement aux six passages du Synopsis guidé de Construction : point de départ, dérèglement et direction, premières actions et conséquences, pression et choix, moment décisif, résultat et changement. Chaque réponse confirmée alimente uniquement le passage correspondant dans `synopsis_answers`. Le synopsis final n’est ni remplacé ni réassemblé automatiquement ; Construction conserve cette action et crée une version du texte précédent lorsque son réassemblage le remplace.

Ces guides utilisent un aperçu confirmé (`app.py:_preview_field_answer`, `_preview_synopsis_answer`, `LearningService.apply_field_answer`, `apply_synopsis_answer`) : destinations en liste fermée, appartenance au projet vérifiée, ajout à la suite par défaut ou remplacement explicite, refus d’une confirmation périmée. Chaque étape propose explication, exemple et question de relecture selon le niveau de guidage. Une étape passée conserve sa réponse éventuelle et reste accessible ; terminer le parcours ne déclare pas les notions acquises. Les réponses, étapes passées et connexions sont conservées à l’export/réimport du projet. Une seule cible par étape reste mémorisée ; les transferts suivants ne synchronisent pas automatiquement la fiche. Les tests dédiés couvrent ces garanties, l’annulation, le rollback et le retour depuis les outils. Aucun changement de schéma SQLite.

Le contrôle antérieur V0.30.3 rapportait 59 tests réussis. Ce résultat n’est pas une nouvelle exécution lors de la clarification documentaire et ne mesure pas la couverture.
Qt hors écran ne remplace pas un contrôle Fedora réel. `tests/test_atomic_persistence.py` protège désormais les échecs d’import/sauvegarde, transactions imbriquées, restauration structurée, échanges de versions et migration additive. Gros projets et fidélité Unicode/FDX restent à approfondir.

## Maintenance de cette source

Pour toute évolution : actualiser la ligne concernée, sa limite, ses symboles et ses tests. Vérifier les symboles dans le code ; ne pas déduire un statut d’une note de version. Les prochaines actions sont uniquement dans [ROADMAP.md](ROADMAP.md).
