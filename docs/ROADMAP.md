# Roadmap canonique

Mise à jour : 7 septembre 2026. Ce document décrit le travail futur, pas des fonctions livrées. L’état actuel est dans [FEATURES.md](FEATURES.md).

## Consolidation issue de l’audit

| Ordre | Chantier | Livrable et critère de sortie |
| --- | --- | --- |
| 1 | Documentation canonique — réalisée | README court, consignes, produit, architecture, décisions, état et roadmap séparés ; anciens textes archivés sans perte. Aucun changement applicatif. |
| 2 | Sécurité des données — prochain chantier | Import validé et atomique ; sauvegarde scénario cohérente ; versions structurées. Tests d’échec, anciennes bases et restauration avant validation. |
| 3 | Hygiène ciblée | Vérifier le manuel suivi et les données qu’il contient, le script ponctuel de localisation et le code IA historique. Aucune suppression globale de sauvegardes. |
| 4 | Frontière apprentissage | Extraire progression/application des widgets, clarifier preuves et maîtrise sans casser la reprise des guides. |
| 5 | Frontière scénario | Consolider modèle canonique et adaptateur Qt avant intégration d’un éditeur avancé ; tests PDF/FDX représentatifs. |
| 6 | Interface et performances | Mesurer changements de vue et images ; extraire uniquement les vues utiles, conserver les garanties d’autosauvegarde. |
| 7 | Index ciblé | Relier fonctionnalités/code/tests et indexer incrémentalement les sources autorisées ; provenance et exclusion des données personnelles. |
| 8 | MCP | Serveur de contexte du repository en lecture seule, sorties limitées ; aucun accès implicite aux histoires. |

Chaque chantier doit rester un changement borné avec tests et retour arrière. Une migration SQLite exige une sauvegarde restaurable : revenir au code précédent seul peut ne pas suffire. Les étapes 2 à 8 ne sont pas engagées par la clarification documentaire.

## Fonctionnalités restantes : numéros d’origine conservés

- Ensemble 2 : guides personnage, conflit, synopsis et outline ; niveaux de guidage à approfondir.
- Ensemble 9 : cartes géographiques, fonds, repères liés aux lieux et terrains. Reporté, pas ajouté implicitement.
- Ensemble 18 : vue géographique après l’ensemble 9 ; cohérence des vues à renforcer.
- Ensemble 19 : éventuelle IA contextualisée à redéfinir. L’ancien professeur est désactivé ; toute réactivation exige une décision explicite, contrôle des données envoyées et accord de l’auteur sur les propositions.
- Ensemble 20 : étendre l’apprentissage connecté existant, pas le réimplémenter.
- Anglais intégral : contenus pédagogiques, formulaires et libellés dynamiques ; préserver les textes utilisateur.
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
