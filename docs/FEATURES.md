# État des fonctionnalités

Vérification statique : 7 septembre 2026, code 0.30.3, base Git `13ed5f5`. « Présent » signifie qu’un chemin de code existe, pas absence de défaut. Tests ci-dessous = points de contrôle existants, pas preuve de couverture exhaustive.

| ID / domaine | État et limite | Code à chercher | Tests existants |
| --- | --- | --- | --- |
| learning.guides | Présent : quatre guides locaux, étapes, réponses et reprise. Catalogue limité. | `learning_content.py`, `content/sessions/`, `app.py:show_learning` | `tests/test_learning_content.py`, `tests/test_ui_smoke.py` |
| learning.application | Partiel : outils et cibles reliés, maîtrise déclarée ; une application par étape et maîtrise globale. | `app.py:_learning_tool_link`, `_save_learning_work`, `db.py:save_guided_application` | `tests/test_v027_connected_learning.py`, `tests/test_database.py` |
| projects | Présent : création, états, archivage, import/export ; import transactionnel avec validation de forme. | `db.py:import_project`, `export_project`, `app.py` | `tests/test_database.py`, `tests/test_ui_smoke.py` |
| ideas | Présent : catégories, images, variantes Et si. | `app.py:show_ideas`, `db.py` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| construction | Présent : documents, cartes, outline, séquences et scènes connectées. | `app.py:show_development`, `_build_scene_list_workspace`, `db.py` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| characters.relations | Présent : fiches, groupes, portraits, références et cartes directionnelles. | `app.py:show_characters`, `RelationshipMapDialog` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| world.locations | Présent : cadre, règles, lexique et lieux connectés ; pas de carte géographique éditable. | `app.py:show_locations`, `db.py` | `tests/test_database.py`, `tests/test_ui_smoke.py` |
| timeline | Présent : pistes et événements, connexions et canevas. Charge importante à tester. | `app.py:TimelineView`, `_timeline_event_dialog` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| narrative.analysis | Présent : arcs, conflits, thèmes, motifs et promesses ; pas d’évaluation IA opérationnelle. | `app.py`, tables associées dans `db.py` | `tests/test_database.py`, `tests/test_v026_overview_export.py` |
| screenplay.editor | Partiel : blocs typés, IDs, raccourcis, complétion et aperçu. Sauvegarde atomique ; nouvelles versions structurées et restauration confirmée. Versions anciennes reconstruites. | `screenplay_model.py`, `app.py:ScreenplayEditor`, `_load_script_document`, `_save_script`, `_snapshot_script` | `tests/test_screenplay_model.py`, `tests/test_screenplay_persistence.py`, `tests/test_editor_polish.py`, `tests/test_layout_followup.py` |
| screenplay.exchange | Partiel : PDF paginé/page de garde, FDX de paragraphes. Pas de FDX sans perte de styles ; PDF limité par cp1252. | `script_export.py` | `tests/test_script_export.py` |
| project.export | Présent : ZIP, PDF de rubriques, scénario et données réimportables ; ne remplace pas toute la base. | `app.py:_build_final_story_export`, `db.py:export_project`, `report_export.py` | `tests/test_report_export.py`, `tests/test_v026_overview_export.py` |
| resources | Présent : genres, glossaire, templates et modèles de fiches. Schémas parfois génériques. | `genres.py`, `template_diagrams.py`, `app.py:show_form_templates` | `tests/test_ui_smoke.py`, `tests/test_database.py` |
| templates.images | Présent : personnalisation globale en settings ; absente de l’export individuel de projet. | `app.py` : chercher `template_image_` | `tests/test_layout_followup.py` |
| search.navigation | Présent : recherche, tags, vues coordonnées et menu Projets repliable. | `app.py:show_search`, `show_story_overview`, `_build_shell` | `tests/test_ui_smoke.py`, `tests/test_layout_followup.py` |
| language | Partiel : libellés anglais, contenus longs et formulaires encore incomplets. | `i18n.py`, appels `tr` dans `app.py` | `tests/test_editor_polish.py` |
| ai.professor | Désactivé : `ask` lève une erreur ; shim et données conservés, ancienne interface et worker retirés. | `ai_service.py:ProfessorAI`, tables historiques dans `db.py` | `tests/test_cleanup.py` vérifie la conservation des données ; service indisponible. |
| geography | Prévu, non implémenté. | Aucun outil géographique dédié identifié. | Pas de garantie existante. |
| repository.mcp | Prévu, non implémenté. | Aucun serveur dans le repository. | À définir avant implémentation. |

## Garanties et limites de validation

Le contrôle antérieur V0.30.3 rapportait 59 tests réussis. Ce résultat n’est pas une nouvelle exécution lors de la clarification documentaire et ne mesure pas la couverture.
Qt hors écran ne remplace pas un contrôle Fedora réel. `tests/test_atomic_persistence.py` protège désormais les échecs d’import/sauvegarde, transactions imbriquées, restauration structurée, échanges de versions et migration additive. Gros projets et fidélité Unicode/FDX restent à approfondir.

## Maintenance de cette source

Pour toute évolution : actualiser la ligne concernée, sa limite, ses symboles et ses tests. Vérifier les symboles dans le code ; ne pas déduire un statut d’une note de version. Les prochaines actions sont uniquement dans [ROADMAP.md](ROADMAP.md).
