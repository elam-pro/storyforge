# StoryForge Desktop 0.30.2 — Corrections éditeur et dossiers PDF

## V0.30.2

- `IN` + Tab → `INT.` ; `E` / `EX` + Tab → `EXT.`. Le lieu et le moment se complètent ensuite séparément.
- Action + Entrée → Personnage ; Nouvelle scène libre crée bien une scène à chaque clic.
- Surimpression des types supprimée ; aperçu scénario structuré dans la vue d’ensemble.
- Export complet : PDF A4 paginés à la place des documents Markdown, sans changer la sauvegarde JSON.
- Groupe Projets repliable, sélection des guides visible, titres et champs harmonisés.
- Bibliothèque de 15 genres et premiers schémas sans rectangles pour les templates.
- Anglais **partiel** : navigation, actions et certains onglets traduits. Les contenus longs et plusieurs formulaires restent en français.

Pour exporter : **Projets → sélectionner un projet → Plus… → Exporter l’histoire terminée…**,
ou le bouton d’export dans **Vue d’ensemble**. Le scénario seul s’exporte depuis l’Éditeur de scripts.

Travaux encore nécessaires : [ROADMAP_REMAINING.md](ROADMAP_REMAINING.md).

StoryForge est une application **Linux locale et gratuite** pour apprendre l’écriture de fiction cinématographique en écrivant.

Le code reste dans le dossier existant `storyforge_desktop_v051`, conformément au choix de conserver un seul dossier de travail.

## V0.30.1 — Correction de l’autocomplétion des scènes

- autocomplétion disponible dès `INT`/`EXT`, même dans un projet sans lieu enregistré ;
- modèles neutres `INT. LIEU` et `EXT. LIEU` proposés comme point de départ ;
- acceptation par `Tab`/`Entrée` sans réouverture du menu ni texte parasite.

## V0.30.0 — Export professionnel et autocomplétion

- autocomplétion locale des en-têtes de scène à partir des lieux et scènes du projet ;
- export FDX avec page de titre configurable et informations de droits ;
- export final avec scénario structuré en JSON, manifeste machine-readable et sauvegarde StoryForge réimportable ;
- scénario, chronologie, personnages, relations, lieux, univers, cartes, scènes et images regroupés dans une archive portable ;
- manifeste et métadonnées du projet inclus pour vérifier rapidement le contenu exporté.

## V0.29.2 — Export scénario

- PDF paginé selon les indents de scénario (scènes, actions, personnages, dialogues et transitions) ;
- page de garde configurable et partagée par les exports PDF/FDX ;
- sauts de page, numéros de page et dialogues poursuivis vérifiés sur plusieurs pages.

## V0.29.1 — SmartType Final Draft

- navigation Tab/Maj+Tab bornée aux six formats sans texte fantôme ;
- suppression progressive entre les formats du scénario ;
- recalcul des mentions `(CONT'D)` après modification des personnages.

## V0.29.0 — Éditeur de scripts visible

- rail de lecture indiquant le type de chaque paragraphe ;
- surlignage de la ligne active ;
- marge dédiée et barre des formats plus lisible ;
- modèle structuré et compatibilité des anciennes sauvegardes préservés.

## V0.28.1 — Éditeur de scripts structuré

- modèle `ScreenplayDocument` indépendant du widget Qt, avec types de blocs et IDs persistants ;
- migration rétrocompatible des scénarios existants depuis le texte historique ;
- représentation JSON conservée dans `script_meta.document_json` sans supprimer `project_docs.content` ;
- conservation du modèle structuré lors des exports et imports de projets ;
- six tests supplémentaires couvrant le modèle et la persistance ;
- aucune nouvelle navigation : l’éditeur existant reste le point d’entrée.

## V0.28.0 — Stabilisation et navigation fluide

- les entrées du panneau latéral conservent une hauteur réservée identique : l’onglet actif ne repousse plus les entrées voisines et ne provoque plus de chevauchement ;
- le changement rapide de projet regroupe les rafraîchissements et ignore les sélections intermédiaires devenues obsolètes ;
- les aperçus d’images des lieux sont chargés après l’affichage du panneau, avec invalidation des aperçus devenus obsolètes ;
- les données SQLite, les connexions existantes et les formats d’export restent inchangés ;
- la suite de tests automatisés reste obligatoire avant chaque commit.

## V0.26.0 — Vue d’ensemble et export final

- nouvel espace **Vue d’ensemble** rattaché au projet actif ;
- six représentations coordonnées : Documents, Plan, Cartes, Chronologie, Relations et Script ;
- filtres communs par recherche, personnage, lieu, statut et tag ;
- double-clic pour ouvrir l’élément dans son outil d’origine, sans créer de copie ;
- export final volontaire dans une archive unique ;
- scénario en PDF, FDX et Fountain, chronologie en Markdown et CSV ;
- fiches Personnages, relations, lieux, univers, règles, thème, conflits, promesses et images ;
- sauvegarde StoryForge complète et réimportable incluse dans l’archive ;
- panneau latéral stabilisé et note de synchronisation des Arcs affichée sur une seule ligne.

## V0.25.0 — Recherche et tags

- recherche globale dans les idées, personnages, relations, lieux, scènes, événements, cartes, séquences, conflits, images, factions et documents ;
- raccourci `Ctrl+K` et accès permanent depuis le panneau latéral ;
- ouverture directe du résultat dans son espace de travail ;
- tags communs au projet, également disponibles dans le Carnet d’idées ;
- filtres par tag dans les idées, personnages, lieux, scènes, séquences, chronologie, conflits et images ;
- gestionnaire central pour créer, colorer, renommer, fusionner et supprimer les tags ;
- conservation des tags et de leurs liens dans les exports/imports de projet.

## V0.24.0 — Modèles de fiches

- nouvel espace **Modèles de fiches**, distinct des templates de structure narrative ;
- interface en trois colonnes : bibliothèque, aperçu de la fiche et réglages ;
- sections et champs réorganisables, duplicables et supprimables ;
- texte court ou long, nombre, date, liste, tags, case à cocher, image et liens internes ;
- modèles assignables séparément à chaque projet et à chaque type de fiche ;
- intégration aux Personnages, Lieux, Scènes, Univers et Thème sans remplacer leurs champs essentiels ;
- conservation des modèles, affectations et valeurs dans les exports/imports de projet ;
- retraits de scénario adaptatifs : toute la largeur disponible participe désormais à la mise en page.

## V0.23.2 — SmartType du scénario

- Tab et Maj+Tab parcourent les formats sans jamais créer de texte à la place de l’auteur ;
- la progression s’arrête aux extrémités au lieu de reboucler de Transition vers Scène ;
- Retour arrière sur un bloc vide suit exactement le chemin inverse : Personnage → Action → Scène ;
- le même retour progressif s’applique à Dialogue, Parenthèse et Transition ;
- `(CONT'D)` est ajouté au second dialogue consécutif du même personnage ;
- les indications comme `(V.O.)` restent conservées avant la mention de continuation.

## V0.23.1 — Mise en forme intelligente

- les six éléments du scénario occupent désormais leur véritable position sur la page ;
- deux pressions sur Tab depuis Scène conduisent visuellement à Personnage ;
- le nom du personnage, les parenthèses, le dialogue et les transitions disposent de retraits distincts ;
- la suppression complète d’un nom de personnage ramène automatiquement le bloc à Action ;
- les autres éléments vides reviennent logiquement au niveau précédent ;
- les changements de format restent immédiats, sans insérer d’espaces artificiels dans le texte.

## V0.23.0 — Écriture du scénario

- éditeur de scénario conservé comme espace d’écriture distinct des documents de préparation ;
- six éléments professionnels : scène, action, personnage, dialogue, parenthèse et transition ;
- scènes préparées et scènes écrites réunies dans une seule liste, dans le même ordre ;
- insertion facultative de la prochaine scène préparée, sans générer son contenu ;
- panneau de contexte repliable : objectif, personnages, lieu, opposition, entrée et sortie ;
- navigation vers la fiche d’un personnage ou la scène correspondante dans Construction ;
- scènes précédente et suivante accessibles depuis le contexte ;
- mode **Concentration** pour masquer toute l’interface autour de la page (`Ctrl+Maj+F`) ;
- sauvegarde automatique, versions, import/export FDX et export PDF toujours disponibles.

## V0.22.1 — Interface harmonisée

- badge du nombre de guides corrigé dans **Guides en cours** ;
- cadres et champs ramenés à une géométrie sobre et cohérente ;
- tailles de texte harmonisées dans les panneaux et les onglets internes ;
- trois niveaux d’action lisibles : principale, secondaire et tertiaire ;
- suppressions définitives visibles dans une variante rouge du troisième niveau ;
- boutons **Annuler** ajoutés aux fiches Personnages et Lieux ;
- actions d’image et de référence renommées, alignées et désactivées lorsqu’elles ne sont pas disponibles.

## V0.22.0 — Scènes connectées

- l’ancienne liste devient un véritable espace de travail **Scènes**, sans créer de module en double ;
- tableau d’ensemble enrichi : numéro, titre, lieu, statut et durée ;
- fiche de scène structurée en **Noyau**, **Déroulement** et **Connexions** ;
- objectif de la scène, objectif du personnage, obstacle, conflit, information révélée, changement, entrée, sortie et notes ;
- statuts progressifs : Idée, À écrire, Brouillon, À revoir et Validée ;
- liens avec personnages, lieux, séquences, chronologie, conflits, thème, motifs, cartes, promesses et moments forts ;
- création facultative depuis le séquencier et ouverture directe de l’Éditeur de scripts ;
- conservation complète des nouvelles données et connexions dans les exports et imports.

## V0.21.1 — Stabilisation de l’interface

- correction du chevauchement provoqué par l’entrée active du panneau latéral ;
- icône de **Conflits** remplacée par un symbole compatible avec les polices Linux ;
- onglets internes plus grands et plus lisibles ;
- bibliothèques de **Personnages** et de **Lieux** élargies ;
- images de Lieux chargées à la demande puis mises en cache pour accélérer les changements de fiche.

## V0.21.0 — Accroche et promesses

- nouvel espace **Accroche et promesses** sous Projets ;
- quatre repères d’accroche : question, situation particulière, attente du spectateur et réponse momentanément retenue ;
- bibliothèque de promesses classables par concept, personnage, conflit, mystère, émotion, univers ou ton ;
- suivi de l’introduction, du développement et de l’accomplissement de chaque promesse ;
- banque de moments désirés : confrontation, révélation, retournement, découverte, émotion, image forte, décision ou climax ;
- connexions aux cartes, séquences, scènes, événements et conflits déjà présents ;
- conversion directe d’un moment en carte de l’histoire, séquence ou scène ;
- vue de contrôle des promesses sans accomplissement et des moments encore non placés ;
- panneau latéral rééquilibré : entrée active plus grande, sous-onglets de Projets alignés et intitulés lisibles.

## V0.20.0 — Arcs et transformations

- nouvel espace **Arcs** sous Projets pour comparer les trajectoires des personnages ;
- tableau d’ensemble : début, épreuve, choix, transformation et situation finale ;
- trajectoire détaillée : croyance initiale, pressions, point de rupture, choix décisif, coût et preuve visible ;
- types d’arcs facultatifs : positif, négatif, stable, tragique ou inachevé ;
- synchronisation avec les informations déjà écrites dans les fiches Personnages ;
- connexions avec scènes, cartes de l’histoire, événements chronologiques et conflits ;
- diagnostic local en six repères, sans imposer une transformation à tous les personnages ;
- export, import et duplication complets ;
- panneau latéral déplié avec icônes et textes, ou replié avec icônes seules.
- intitulés du panneau latéral agrandis pour rester lisibles sur un écran de bureau.

## V0.19.2 — Panneau latéral compact

- nouveau bouton dans la barre supérieure pour déplier ou replier le rail de navigation ;
- raccourci `Ctrl+B` ;
- état déplié ou replié conservé entre deux lancements.

## V0.19.1 — Interface Studio

- nouvelle barre supérieure compacte avec marque, projet actif et accès aux projets ;
- navigation verticale réduite à des icônes, avec le nom complet de chaque espace au survol ;
- ambiance studio anthracite et accent rouge-orangé, sans effet « tableau de bord IA » ;
- panneaux, champs et boutons plus droits, plus discrets et plus denses ;
- Personnages et Lieux utilisent directement toute la hauteur disponible en trois colonnes harmonisées ;
- l’apparence sombre Studio est activée au premier lancement de cette version, tout en conservant le mode clair dans Paramètres.

## V0.19.0 — Conflits connectés

- nouvel onglet **Conflits** sous Projets, avec recherche et filtres par importance et nature ;
- conflits principaux ou secondaires, externes, internes, relationnels, sociaux ou liés au monde ;
- fiche organisée en **Noyau**, **Forces**, **Progression** et **Connexions** ;
- objectifs incompatibles, enjeux et motivations propres aux deux forces ;
- stratégie, avantage, vulnérabilité et perte redoutée pour chaque camp ;
- personnages et groupes/factions assignables séparément aux deux côtés ;
- progression complète : déclenchement, premières actions, aggravation, options qui disparaissent, choix difficile et confrontation décisive ;
- résolution structurée : résultat, victoire, perte, prix payé et changement produit ;
- connexions avec scènes, cartes de l’histoire, événements chronologiques et positions thématiques ;
- préremplissage facultatif depuis le protagoniste, l’objectif, l’opposition, les enjeux et la Carte de l’histoire déjà renseignés ;
- diagnostic local en cinq repères, sans déclarer automatiquement un conflit « valide » ;
- export, import et duplication de toutes les informations et connexions ;
- trente-six tests automatisés.

## V0.18.0 — Thème et motifs

- nouvel onglet **Thème** sous Projets, entièrement facultatif et propre au projet actif ;
- espace **Question** pour formuler le thème général, la question centrale, l’intérêt personnel et la morale trop simple à éviter ;
- espace **Positions** pour confronter une position principale, une opposition et des réponses nuancées ;
- chaque position peut être portée par un ou plusieurs personnages existants ;
- espace **Expression** pour observer le thème à travers les décisions, conséquences, conflits et la réponse suggérée par la fin ;
- bibliothèque de **Motifs** : objets, lieux, images, comportements, événements, couleurs ou sons récurrents ;
- chaque motif conserve son sens possible, ses apparitions et son évolution ;
- connexions facultatives des motifs avec les lieux, événements chronologiques et images du projet ;
- export, import et duplication du thème, des positions, des personnages associés, des motifs et de toutes leurs connexions ;
- fonctionnement local sans IA, clé API ni abonnement ;
- trente-quatre tests automatisés couvrent désormais l’application.

La refonte graphique générale envisagée précédemment est volontairement mise en attente : cette version se concentre sur le nouvel outil narratif et conserve l’interface actuelle.

## V0.16.0 — Lieux connectés au projet

- nouvel onglet **Lieux** sous Projets, avec sélection du projet actif ;
- bibliothèque recherchable, filtrable par catégorie et réorganisable ;
- fiche complète sans devenir encyclopédique : identité, région, époque, tags, description, fonction narrative, atmosphère, contraintes, évolution et notes ;
- grande image de couverture et références visuelles réutilisant la bibliothèque d’images du projet ;
- connexions avec personnages, événements de la Chronologie, scènes et images ;
- export, import et duplication des lieux avec toutes leurs connexions ;
- liste Personnages alignée sur Lieux à 285 px, silhouette agrandie et fiche légèrement réduite ;
- Personnages est désormais un sous-onglet de Projets, comme Construction, Chronologie, Univers et Lieux ;
- champs narratifs de Lieux bordés et lignes de connexion entièrement cliquables ;
- coins du canevas Chronologie réellement arrondis, y compris autour des barres de défilement ;
- Carte de l’histoire mobile à la souris et Chronologie débarrassée de son extension vide à droite.

## V0.15.0 — Univers et cohérence du travail

- nouvel onglet **Univers** sous Projets, organisé en Cadre, Règles, Histoire et Lexique ;
- l’Histoire du monde réutilise les événements Monde, Guerre et Backstory de la Chronologie ;
- chaque règle peut préciser son champ d’application, ses limites, son coût, ses exceptions et sa conséquence dramatique ;
- chaque règle peut être reliée aux personnages, groupes/factions, événements chronologiques et images concernés ;
- **Guides en cours** est un sous-espace de Guides d’écriture dans la barre latérale ;
- nouveau **Glossaire** général, filtrable par catégorie, distinct du lexique propre à un projet ;
- Templates basculables entre une lecture traditionnelle et un schéma visuel en lecture seule ;
- filtres de recherche et de catégorie dans Images ;
- silhouettes Femme/Homme, rôles sous forme de liste et champs Personnages harmonisés ;
- cartes de l’histoire et événements chronologiques disposent désormais de sélections de personnages explicites ;
- la Carte de l’histoire se parcourt librement en faisant glisser le fond et conserve ses quatre coins arrondis ;
- la Chronologie garde une marge droite stable après l’ajout ou la suppression d’un événement ;
- un double-clic sur un projet ouvre sa Construction sur **Prémisse / Concept** ;
- les cellules d’édition de la Liste de scènes sont plus hautes ;
- choix initial Français/English dans Paramètres.

## V0.14.1 — Chronologies libres et idées élargies

- un projet peut contenir plusieurs timelines visibles simultanément : intrigue principale, backstory, monde ou toute ligne libre ;
- chaque timeline possède un nom, une couleur et peut être renommée ou supprimée sans perdre ses événements ;
- le canevas se déplace réellement dans les quatre directions avec la souris et conserve de larges marges de travail ;
- un double-clic sur un événement ouvre directement sa fiche ;
- la fiche événement affiche des champs encadrés et une liste de personnages clairement cochable ;
- le carnet d’idées contient une étape **Élargir avec « Et si ? »** pour conserver plusieurs variantes sans choisir trop tôt ;
- la fiche Personnages affiche les intitulés complets de ses six onglets ;
- timelines, couleurs et rattachements des événements sont préservés lors des exports, imports et duplications ;
- trente tests automatisés vérifient désormais l’ensemble.

## V0.14.0 — Carte des relations

- le bouton **Relations** ouvre désormais un véritable diagramme visuel ;
- chaque personnage apparaît comme un nœud avec son portrait, son nom, son rôle et ses groupes ;
- les portraits se déplacent librement et leur position est enregistrée automatiquement ;
- les relations sont directionnelles : deux personnages peuvent donc éprouver deux relations différentes l’un envers l’autre ;
- les flèches portent un nom et une couleur selon le type : amour, amitié, famille, rivalité, haine, respect, méfiance, manipulation, autorité, secret ou alliance ;
- chaque relation conserve description, tension, secret et évolution ;
- plusieurs cartes indépendantes sont possibles, avec des raccourcis pour Famille, Travail, Début et Fin de l’histoire ;
- filtres par personnage et par groupe/faction ;
- canevas quadrillé, déplaçable, zoomable et extensible automatiquement quand un portrait sort du cadre ;
- cartes, positions et relations complètes sont conservées dans les exports, imports et duplications de projet ;
- les anciennes relations sont migrées vers **Relations générales** sans perte.

### Ajustement Personnages

- la colonne de liste est maintenant plus étroite ;
- la silhouette/moodboard et la fiche disposent de davantage de largeur.

## V0.13.2 — Personnages équilibrés et chronologie mobile

- l’espace **Personnages** utilise trois colonnes de même importance : liste, silhouette/références et fiche ;
- le bandeau redondant de sélection a disparu ; la liste de gauche choisit directement le personnage actif ;
- la liste conserve sa propre recherche, son filtre par rôle et son défilement pour accueillir une grande distribution ;
- la fiche est plus compacte et ses six onglets restent accessibles sans débordement ;
- les éditeurs multilignes, groupes, connexions et champs personnalisés possèdent désormais une bordure visible ;
- la silhouette ou l’image reste entièrement visible quand la fenêtre ou la colonne change de taille ;
- la **Chronologie** se parcourt à la souris en faisant glisser son fond, avec `Maj + molette` comme raccourci horizontal.

## V0.13.1 — Ensemble 5 : Personnages approfondis

- rôles structurés : protagoniste, antagoniste, allié, opposition, secondaire, figurant ou groupe/faction, avec saisie libre toujours possible ;
- création de familles, équipes, factions, entreprises, royaumes, gangs ou autres groupes, puis rattachement d’un personnage à plusieurs groupes ;
- bibliothèque compacte adaptée aux distributions nombreuses, avec recherche et filtres séparés par rôle et par groupe ;
- moodboard propre à chaque personnage : plusieurs images de référence, aperçu immédiat et choix d’une référence comme portrait ;
- champs personnalisés facultatifs pour conserver une information propre au projet sans alourdir toutes les fiches ;
- onglet **Connexions** listant les scènes, cartes de l’histoire et événements chronologiques associés au personnage ;
- désir, objectif et besoin restent trois informations distinctes ; l’onglet Arc conserve la comparaison entre situation de départ, transformation et situation finale ;
- groupes, références et champs libres sont conservés lors des exports, imports et duplications de projet.

## V0.13.0 — Chronologie et nouvelle fiche Personnages

- **Chronologie** place les événements en années, mois, jours ou heures sur des lignes thématiques ;
- chaque événement conserve son nom, son repère, sa catégorie, son lieu, sa description, ses conséquences et ses personnages ;
- la même histoire peut être filtrée en vue complète, intrigue principale, backstory ou chronologie d’un personnage ;
- **Personnages** utilise désormais un sélecteur compact : même avec plusieurs dizaines de fiches, la page de travail reste dégagée ;
- une bibliothèque ouvrable propose recherche, filtres par rôle et grille de sélection ;
- la fiche active réunit une grande silhouette ou image de référence et quatre onglets : Essentiel, Dramaturgie, Arc, Voix & notes ;
- les champs existants sont préservés et complétés sans supprimer les anciennes données ;
- portraits, événements et connexions sont inclus dans l’export, l’import et la duplication des projets.

## V0.12.0 et V0.12.1 — Plan global et connexions

- l’étape **08 · Plan global** réunit sections libres, séquences, beats et scènes dans une même hiérarchie ;
- aucun acte n’est créé ou imposé automatiquement ;
- déplacement par glisser-déposer, changement de niveau, repli/dépli, recherche et zoom de lecture ;
- bascule entre vue compacte et vue détaillée ;
- ajout, duplication et suppression d’un élément sans supprimer sa source ;
- transformation d’un beat libre en scène réelle ;
- lien facultatif avec une carte de l’histoire ;
- synchronisation locale dans les deux sens avec le séquencier et la liste de scènes ;
- accès direct à la séquence, la scène ou la carte liée ;
- diagnostic local des informations élémentaires manquantes ;
- hiérarchie et connexions conservées lors des exports/imports ;
- vingt-sept tests automatisés.

## V0.11.0 et V0.11.1 — Parcours guidés indépendants

- nouvel espace **Guides d’écriture** réunissant les parcours en cours et les guides disponibles ;
- sélecteur permanent **Projet actif** en bas de la barre latérale pour changer de contexte depuis n’importe quel espace ;
- chaque graine possède désormais ses propres réponses et sa propre progression ;
- migration automatique de l’ancien Chemin de la graine sans supprimer son contenu ;
- reprise, archivage et progression séparés pour chaque parcours ;
- trois niveaux d’aide : Découverte, Guidé et Autonome ;
- nouveau guide **Renforcer une idée**, appliquable à la prémisse après prévisualisation ;
- nouveau guide **Trouver une fin provisoire**, relié à la fin du projet et à la résolution de la carte ;
- nouveau guide **Préparer une scène**, relié à la Liste de scènes sans créer de doublon lors d’une nouvelle application ;
- application contrôlée : StoryForge montre la version actuelle et la proposition avant toute modification ;
- parcours inclus dans l’export et la duplication du projet ;
- fonctionnement entièrement local, sans IA, jeton ou abonnement.

## V0.10.0 — Création et gestion des projets

- nouvelle fenêtre de création avec titre, support, format et durée cible ;
- formats Micro-film, Court métrage, Moyen métrage, Long métrage et Durée libre ;
- choix explicite entre le Chemin de la graine et une création libre dans Construction ;
- un projet guidé n’est créé qu’après la graine, afin de ne pas produire une fiche vide prématurément ;
- recherche instantanée, filtre par statut et tri par modification, création ou titre ;
- statuts En cours, En pause et Terminé, indépendants de la progression narrative ;
- duplication complète des documents, cartes, séquences, scènes, personnages, relations, images et versions ;
- archivage réversible et suppression définitive uniquement depuis les archives ;
- date de dernière modification mise à jour par les différents outils du projet ;
- liste enrichie sans ajouter un second tableau de bord ni mélanger Projets et Construction.

## V0.9.1 à V0.9.3

### Éditeur professionnel — V0.9.1

- import de scénarios Final Draft (`.fdx`) avec conservation automatique de la version remplacée ;
- page de titre avec titre, auteur, version/date et contact ;
- raccourcis `Ctrl+1` à `Ctrl+6` pour les six types de paragraphes et `Ctrl+S` pour enregistrer ;
- tabulations intelligentes, passage automatique au type logique après Entrée et indication de la page courante ;
- export FDX enrichi et export PDF avec page de titre, numérotation et groupes de dialogues protégés contre les mauvaises coupures.

### Scènes avancées — V0.9.2

- réorganisation verticale des scènes par glisser-déposer ;
- objectif, opposition et changement propres à chaque scène ;
- durée totale calculée automatiquement ;
- transformation facultative du séquencier en premières scènes, sans créer de doublons ;
- association des personnages présents à chaque scène.

### Personnages connectés — V0.9.3

- relations entre personnages avec type, description et tension ;
- présence des personnages reliée aux scènes ;
- personnages associés directement aux cartes de l’histoire ;
- toutes ces connexions sont locales et incluses dans l’export/import du projet.

### Ajustements conservés de la V0.9.1

- Dans le **Chemin de la graine**, Enregistrer ne signifie plus Terminer : un bouton **Pas terminé** conserve explicitement l’étape en brouillon.
- Dans **Construction**, chaque document possède maintenant deux états explicites : **Pas fini** ou **Terminé**. Le contenu reste enregistré dans les deux cas.
- Les anciennes coches ont été migrées afin de préserver la progression existante.
- L’en-tête du Synopsis sépare désormais le compteur de réponses de la barre de progression et compacte les six questions sans chevauchement.
- Dans l’Éditeur de scripts, `Tab` passe au type suivant et `Maj + Tab` revient au précédent : Scène → Action → Personnage → Dialogue → Parenthèse → Transition.
- Après Entrée, l’éditeur choisit aussi le type naturel suivant, par exemple Personnage → Dialogue.

## Nouveaux espaces de la V0.9.0

- **Projets** affiche une seule liste sur toute la largeur ; **Construction** est maintenant son sous-espace et possède son propre sélecteur de projet.
- **Personnages** conserve une bibliothèque de fiches séparée pour chaque projet.
- **Images** conserve une bibliothèque visuelle séparée pour chaque projet.
- **Idées** propose une grande zone d’image avec un `+` central et un aperçu réel de la référence choisie.
- **Liste de scènes** devient un tableau avec numéro, titre et durée estimée.
- **Scénario** résume la préparation puis ouvre le nouvel **Éditeur de scripts**.
- La catégorie **Écriture** rassemble désormais l’Éditeur de scripts et la Réécriture.
- Le scénario est enregistré localement, navigable par scènes, versionnable et exportable en **FDX** ou **PDF**.
- Les scènes, personnages et images sont inclus dans l’export et l’import d’un projet.

## Éditeur de scripts

L’éditeur reconnaît une mise en page légère directement lisible :

- `INT.` ou `EXT.` pour une scène ;
- une phrase ordinaire pour une action ;
- un nom en majuscules pour un personnage ;
- une ligne entre parenthèses pour une indication brève ;
- les transitions usuelles comme `COUPE À :`.

Les anciens marqueurs Fountain `!` et `@` restent compris lors d’un import, mais les boutons n’en ajoutent pas à l’écran. Les boutons Scène, Action, Personnage, Dialogue, Parenthèse et Transition insèrent les éléments sans obliger à mémoriser la mise en page. La colonne de gauche retrouve automatiquement les scènes et permet de naviguer dans le premier jet.

Depuis l’intégration du modèle structuré, l’éditeur conserve aussi chaque bloc
et son type dans `script_meta.document_json` (schéma versionné). Le champ
`project_docs.content` reste une projection texte compatible avec les projets
existants et les exports. Les migrations sont automatiques et réversibles par
la sauvegarde SQLite habituelle.

## Plan global et séquencier détaillé

L’étape **08 · Plan global** affiche d’abord toute l’histoire dans une arborescence modifiable :

- sections libres pour nommer les grandes parties sans imposer des actes ;
- séquences, beats et scènes dans le même ordre de lecture ;
- glisser-déposer et boutons de niveau pour créer la hiérarchie utile au projet ;
- repli, recherche, zoom, vues compacte et détaillée ;
- colonnes adaptées aux séquences et scènes : contenu/opposition, fonction/objectif, conséquence/changement ;
- liens visibles vers la Carte de l’histoire, le séquencier et la Liste de scènes ;
- diagnostic simple, entièrement local et sans IA.

Le bouton **Séquencier détaillé** conserve l’ancienne vue verticale spécialisée :

- une séquence par bloc ;
- déplacement vertical avec la poignée `≡` ;
- titre, fonction narrative, événements et conséquence ;
- ajout, duplication et suppression ;
- sauvegarde locale automatique et reprise dans le même ordre ;
- transformation facultative des cartes renseignées de la Carte de l’histoire ;
- ordre causal des cartes reliées, avec ordre spatial comme repère de secours ;
- prévention des doublons lorsqu’une carte a déjà été importée ;
- séquences incluses dans les exports et imports de projet.

L’ancien contenu libre de l’outline n’est pas perdu : à la première ouverture, il devient une séquence importée et modifiable.

## Banque de templates

La nouvelle catégorie **Ressources** contient l’onglet **Templates**. La banque propose des points de départ facultatifs :

- colonne vertébrale causale ;
- court métrage concentré ;
- trois actes comme repère souple ;
- quatre mouvements ;
- Story Circle ;
- huit séquences ;
- voyage du héros ;
- Kishōtenketsu ;
- mystère et révélation ;
- transformation d’une relation ;
- Robert McKee — valeurs et progression ;
- John Truby — 7 repères essentiels ;
- Save the Cat en 15 beats.

Chaque fiche indique quand l’outil peut aider et ce qu’il ne faut pas forcer. Un clic ajoute ses repères comme blocs entièrement modifiables au séquencier du projet actif. Aucun template ne valide une histoire et aucun modèle n’est obligatoire.

## Construction

L’ancien espace **Documents** s’appelle désormais **Construction**. La prémisse, la logline, le résumé, le synopsis et les autres textes conservent leur éditeur guidé.

**Carte de l’histoire** ouvre maintenant un véritable tableau visuel :

- cartes colorées et déplaçables ;
- types Situation, Événement, Objectif, Action, Obstacle, Conséquence, Choix, Résolution ou Idée libre ;
- modification par double-clic ;
- liens orientés cause → conséquence ;
- suppression des cartes ou des liens sélectionnés ;
- déplacement, zoom et défilement du tableau ;
- extension automatique du canevas lorsqu’une carte approche d’un bord ;
- grande zone vide disponible sans placer une carte à l’extrémité ;
- extension supplémentaire lorsque l’on parcourt les limites de cette zone vide ;
- défilement automatique de la vue pendant le glisser-déposer ;
- auto-défilement différé pour éviter toute réentrée ou tout crash du moteur graphique Qt ;
- nettoyage intégral du canevas pendant le déplacement pour éviter les fragments de courbes sous Linux ;
- positions et connexions enregistrées localement ;
- cartes et liens inclus dans les exports de projet.

Le guide causal en neuf questions reste accessible avec le bouton **Guide**. Ses réponses existantes sont transformées en cartes reliées lors de l’ouverture de la vue visuelle.

## Synopsis guidé

L’étape **05 · Synopsis** est maintenant un véritable parcours de construction :

- six questions, affichées une par une ;
- deux repères pour le début, deux pour le développement et deux pour la fin ;
- reprise automatique des réponses de la Carte de l’histoire et des cartes renseignées ;
- matière proposée entièrement modifiable avant enregistrement ;
- assemblage des six passages en un texte continu sans titres d’actes ;
- grand éditeur final avec sauvegarde locale et création de versions ;
- retour libre entre le guide et le texte final ;
- réassemblage facultatif en conservant la version précédente ;
- réponses guidées incluses dans l’export et l’import du projet.

Les trois parties servent seulement à ne pas oublier le point de départ, la progression et le résultat. Elles n’imposent ni trois actes ni longueur prédéfinie.

## Parcours détaillé

L’onglet **Parcours** présente maintenant une seule phase à la fois :

- Cycle 0 — Fondations dramatiques ;
- Court 1 — Premier court guidé ;
- Court 2 — Autonomie progressive ;
- Long — Projets plus longs.

Chaque phase précise son objectif, son livrable, le critère permettant de passer à la suite et son processus détaillé. Les 38 sous-étapes expliquent ce qu’il faut faire et le résultat concret attendu. Un bouton ouvre ensuite directement l’espace StoryForge correspondant.

Le détail apparaît dans un seul grand panneau déroulant. Les sous-étapes sont séparées visuellement sans être enfermées dans une succession de cartes.

## Carte de l’histoire causale

La priorité de la V0.7 est un parcours en neuf questions :

1. situation de départ ;
2. événement qui dérègle la situation ;
3. objectif ;
4. premières actions ;
5. obstacles et conséquences ;
6. aggravation ;
7. choix difficile ;
8. confrontation finale ;
9. résolution et changement.

Dans le guide optionnel, StoryForge ne montre qu’une seule question et une seule zone d’écriture à la fois. Chaque fiche explique pourquoi la question compte, définit le mécanisme utile et fournit un exemple court. Aucun découpage en trois actes ni aucune beat sheet n’est imposé.

L’objectif ou les réponses universelles déjà présents dans le projet sont repris lorsque cela évite une ressaisie. Chaque réponse reste modifiable. La progression est enregistrée localement et la dernière étape produit une synthèse causale complète dans le document **Carte de l’histoire**.

Si une ancienne carte libre existe, elle est conservée dans l’historique avant la première synthèse structurée.

## Autres documents de développement

La catégorie **Développer** permet de construire le projet actif dans un ordre progressif :

1. Prémisse / Concept ;
2. Logline ;
3. Résumé très court ;
4. Carte de l’histoire ;
5. Synopsis ;
6. Treatment ;
7. Carte de beats ;
8. Plan global ;
9. Liste de scènes ;
10. Scénario.

Les documents textuels conservent une fiche pédagogique compacte et un grand éditeur. La Carte de l’histoire, le Synopsis et le Plan global disposent de leurs espaces visuels ou guidés propres.

Les actions restent fixes sous l’éditeur : document précédent, enregistrement local, création d’une version et passage au document suivant. Une coche apparaît dans la navigation dès qu’un document contient du texte.

Les résumés, synopsis, treatments, beats, séquenciers, listes de scènes et scénarios déjà présents sont réutilisés. La V0.7 ajoute simplement les nouveaux documents Prémisse, Logline et Carte de l’histoire au même projet, sans dupliquer les données.

## Guides d’écriture

L’ancien **Chemin de la graine** devient le premier parcours de l’espace **Guides d’écriture**. Il transforme progressivement une idée en graine d’histoire, mais chaque nouvelle graine est maintenant isolée des précédentes.

La page d’accueil des guides permet de reprendre ou d’archiver un parcours et d’en démarrer un autre. Trois quantités d’aide sont disponibles à tout moment :

- **Découverte** : définition, exemple et repères ;
- **Guidé** : question et rappel court ;
- **Autonome** : question et livrable uniquement.

Le chemin avance une question à la fois. Le panneau de progression reste à gauche. À droite :

- une fiche courte avec la question, l’objectif, la définition, un exemple et des repères ;
- un grand champ d’écriture avec ascenseur toujours visible ;
- une barre d’actions séparée, sans chevauchement en mode fenêtré.

Les quatorze étapes couvrent l’idée, le protagoniste, le désir, l’objectif, l’opposition, les enjeux, les actions, les conséquences, la progression, le choix, le changement, la fin et la graine d’histoire.

## Synthèse et création du projet

Après la dernière étape, StoryForge affiche une synthèse déroulante :

- idée de départ ;
- protagoniste ;
- désir et objectif ;
- opposition et enjeux ;
- choix difficile ;
- changement ;
- fin possible ;
- graine d’histoire.

Le bouton **Créer le projet** demande seulement un titre provisoire. StoryForge copie ensuite les réponses dans un nouveau projet et place la graine dans **01 · Prémisse / Concept**. Le parcours reste consultable et se rattache au projet créé.

## Projets alignés sur Construction

L’espace **Projets** ne possède plus une progression concurrente en Noyau, Développement et Prochaine action. Chaque histoire reprend directement les dix étapes de **Construction** :

1. Prémisse / Concept ;
2. Logline ;
3. Résumé très court ;
4. Carte de l’histoire ;
5. Synopsis ;
6. Treatment ;
7. Carte de beats ;
8. Plan global ;
9. Liste de scènes ;
10. Scénario.

La liste de projets affiche la progression réelle et la première étape incomplète. Le bouton **Ouvrir Construction** active le projet puis ouvre son espace de développement. Les anciens repères — protagoniste, désir, objectif, opposition, enjeux, changement, fin et notes de travail — restent accessibles dans une fenêtre secondaire sans créer une deuxième feuille de route.

## Écriture et réécriture

La catégorie **Écriture** sépare clairement deux moments :

- l’Éditeur de scripts pour produire et exporter le premier jet ;
- Réécriture pour relire les instantanés créés avant chaque passe importante.

L’ancien Atelier reste compatible dans le code avec les bases existantes, mais il n’encombre plus la navigation principale.

## Données et utilisation locale

Les réponses de chaque guide sont conservées séparément. Les anciennes données V0.4 à V0.10 sont préservées et l’ancienne session de graine est migrée automatiquement. Le professeur IA payant et ses réglages ne figurent pas dans l’interface ; aucun jeton, abonnement ou service en ligne n’est requis.

## Installation Linux

Prérequis : Python 3.11 ou plus récent.

```bash
chmod +x run_linux.sh
./run_linux.sh
```

Le premier lancement crée `.venv` et installe uniquement PySide6.
