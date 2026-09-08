# Roadmap canonique

Mise à jour : 9 septembre 2026. Ce document sépare les chantiers de consolidation achevés du travail futur. L’état actuel est dans [FEATURES.md](FEATURES.md).

## Consolidation issue de l’audit

| Ordre | Chantier | Livrable et critère de sortie |
| --- | --- | --- |
| 1 | Documentation canonique — réalisée | README court, consignes, produit, architecture, décisions, état et roadmap séparés ; anciens textes archivés sans perte. Aucun changement applicatif. |
| 2 | Sécurité des données — réalisée | Import validé et atomique ; sauvegarde scénario cohérente ; versions structurées. Tests d’échec, ancienne table de versions et restauration sur bases temporaires. |
| 3 | Hygiène ciblée — réalisée | Manuel généré hors sources et ancien fichier local dé-suivi ; script ponctuel archivé en texte ; interface IA désactivée et rail masqué retirés. Shim, données, sauvegardes et historique Git conservés. Contenu privé éventuel de l’ancien historique non audité ni purgé. |
| 4 | Frontière apprentissage — extraction réalisée | Réponses, progression, applications et maîtrise explicite extraites dans LearningService, testées sans Qt et avec les outils existants. Le choix des cibles/navigation reste dans l’interface. Une évolution vers plusieurs preuves contextualisées reste une décision produit distincte ; les règles actuelles sont conservées. |
| 5 | Frontière scénario — consolidation réalisée | Validation JSON/version/IDs ; règles de commande et retraits isolés ; FDX typé et PDF Unicode testés. Fidélité limitée au périmètre documenté, pas de Final Draft sans perte ni nouvel éditeur. |
| 6 | Interface et performances — réalisée | Mesures sur fixtures, caches bornés et décodage réduit ; tests de navigation et sauvegarde conservés. Aucun remaniement global des vues non justifié par les mesures. |
| 7 | Index ciblé — réalisé | Sources autorisées et suivies par Git, reparsing incrémental en mémoire, liens fonctionnalités/code/tests, provenance et limites testées. |
| 8 | MCP — implémenté et testé | Sept outils et cinq ressources STDIO en lecture seule ; configuration locale préparée. Chargement dans Codex en attente de l’autorisation du projet par l’utilisateur ; voir MCP.md. |

Chaque chantier reste un changement borné avec tests et commit local. Les phases 5 à 8 ont été explicitement demandées, sans migration SQLite supplémentaire. Une future migration exige une sauvegarde restaurable : revenir au code précédent seul peut ne pas suffire. L’autorisation de confiance Codex n’est pas modifiée automatiquement.

## Fonctionnalités restantes : numéros d’origine conservés

- Ensemble 2 : niveaux de guidage à approfondir. Les guides Personnage, Conflit, Synopsis et Plan détaillé sont livrés, voir FEATURES.md.
- Ensemble 9 : cartes géographiques, fonds, repères liés aux lieux et terrains. Reporté, pas ajouté implicitement.
- Ensemble 18 : vue géographique après l’ensemble 9 ; cohérence des vues à renforcer.
- Ensemble 19 : IA reportée à la demande de l’utilisateur. L’ancien professeur est désactivé ; toute réactivation exige une décision explicite, contrôle des données envoyées et accord de l’auteur sur les propositions.
- Ensemble 20 : étendre l’apprentissage connecté existant, pas le réimplémenter.
- Anglais intégral : reporté à la demande de l’utilisateur ; contenus pédagogiques, formulaires et libellés dynamiques à compléter plus tard, sans traduire les textes utilisateur.
- Templates : illustrations pédagogiques distinctes par modèle ; la personnalisation existe, les schémas restent parfois génériques.
- Qualité : longs projets, images volumineuses, petites fenêtres, navigation avec modifications en attente et deux langues.

## Validation prioritaire de la phase 2

1. Base temporaire et fixtures anciennes, jamais la base personnelle.
2. Import invalide ou interrompu : aucune écriture partielle.
3. Sauvegarde interrompue : texte et JSON cohérents.
4. Version restaurée : types, IDs et métadonnées préservés dans le périmètre défini.
5. Export/réimport : liens et isolation des projets conservés.
6. Tests ciblés puis suite complète ; compte rendu des tests ignorés et du retour arrière.

Le détail historique des ensembles et la référence visuelle initiale restent dans [l’ancienne roadmap](archive/ROADMAP_REMAINING.pre-canonical-2026-09-07.md), non normative.
