# Travail postérieur à StoryForge 0.30.3 — Consolidation

- audit canonique du produit, de l’architecture, des décisions, des fonctionnalités et de la roadmap ;
- huit guides locaux reliés aux outils, avec niveaux d’aide explicites et historique des applications/relectures ;
- diagrammes natifs distincts pour les treize templates, tout en conservant les images personnalisées prioritaires et réversibles ;
- cartes géographiques multiples dans **Univers**, liées aux lieux et images existants, avec panoramique, zoom, repères déplaçables et export/réimport ;
- caches d’images bornés, décodage réduit, benchmarks et parcours de captures sur bases temporaires ;
- MCP de contexte local en lecture seule configuré et validé avec ses sept outils et cinq ressources ;
- 144 tests automatisés réussis ; anglais intégral et IA volontairement reportés.

# StoryForge 0.30.3 — Correctifs d’affichage ciblés

- Rétablissement des marges extérieures sur les trois pages signalées.
- Centrage de la page de scénario en lecture seule.
- Positionnement du popup à partir des coordonnées globales du viewport, hors de la ligne de saisie.
- Images personnalisées par template, copie intégrée dans SQLite, validation et retour au schéma fourni.
- Tests de géométrie, acceptation par Tab et persistance des images sans leur fichier source.

# StoryForge 0.30.2 — Stabilisation éditeur et PDF

- Complétion progressive des préfixes, lieux et moments ; retour Action → Personnage.
- Création répétée de scènes avec types conservés, suppression du rail superposé au texte.
- Aperçu structuré du scénario et documents de l’export complet convertis en PDF Unicode paginés.
- Navigation Projets repliable et mémorisée, indication du guide sélectionné, espacement des titres et tailles de champs cohérentes.
- Bibliothèque de genres consultable et remplacement des rectangles des templates par des repères visuels.
- Catalogue anglais initial, volontairement sans traduction automatique des textes de l’auteur. **Traduction intégrale non terminée.**
- Les visuels propres à chaque structure restent à enrichir ; voir `ROADMAP_REMAINING.md`.

# StoryForge 0.30.1 — Correction de l’autocomplétion des scènes

## V0.30.1

- les préfixes `INT`, `EXT` et `I/E` sont reconnus avant la saisie du point ;
- un projet neuf propose des modèles de lieux neutres ;
- `Tab` et `Entrée` valident une suggestion sans texte fantôme ni popup persistant.

# StoryForge 0.30.0 — Export professionnel et autocomplétion

## V0.30.0

- autocomplétion locale des en-têtes de scène à partir des lieux et scènes du projet ;
- FDX enrichi avec page de titre optionnelle, adaptation et mentions de droits ;
- export final enrichi d’un manifeste JSON et d’une représentation structurée du scénario ;
- cartes de l’histoire exportées en Markdown/CSV avec connexions, personnages liés et positions ;
- métadonnées du projet exportées séparément pour contrôler le contenu de l’archive ;
- types de paragraphes préservés dans les exports finaux au lieu d’une nouvelle détection heuristique.

# StoryForge 0.29.2 — Export scénario

## V0.29.2

- mise en page PDF scénario et pagination professionnelle conservées et vérifiées ;
- page de garde configurable partagée par les exports PDF et FDX ;
- numérotation et continuation des dialogues vérifiées sur plusieurs pages.

# StoryForge 0.29.1 — SmartType Final Draft

## V0.29.1

- tabulations et retours restent bornés aux six formats sans créer de texte parasite ;
- suppression progressive conservée entre Personnage, Action et Scène ;
- `(CONT'D)` est recalculé après une modification, un renommage ou une suppression de personnage ;
- les marqueurs de continuation obsolètes sont automatiquement retirés ;
- les données structurées et les exports existants restent compatibles.

# StoryForge 0.29.0 — Éditeur de scripts visible

## V0.29.0

- ajout d’un rail de lecture non éditable indiquant le type de chaque paragraphe : scène, action, personnage, dialogue, parenthèse ou transition ;
- surlignage de la ligne active pour suivre immédiatement la position du curseur ;
- marge de lecture dédiée à gauche du manuscrit afin d’éviter que les types et le texte se mélangent ;
- barre des six formats agrandie et raccourcis affichés dans les info-bulles ;
- modèle structuré et compatibilité des anciennes sauvegardes conservés.

# StoryForge 0.28.1 — Éditeur de scripts structuré

## V0.28.1

- intégration du modèle `ScreenplayDocument` dans l’Éditeur de scripts déjà présent ;
- types de paragraphes conservés séparément du widget Qt : scène, action, personnage, dialogue, parenthèse et transition ;
- IDs persistants pour les blocs et sérialisation JSON versionnée ;
- migration SQLite rétrocompatible via `script_meta.document_json` ;
- export/import de projet StoryForge préservant la représentation structurée ;
- aucune nouvelle navigation ni aucun parcours ajouté.

---

# StoryForge 0.28.0 — Stabilisation et navigation fluide

## V0.28.0

- hauteur réservée identique pour les entrées du panneau latéral afin d’éviter les chevauchements lors du changement d’onglet ;
- rafraîchissement de projet différé et regroupé pour éviter les reconstructions intermédiaires lors d’un changement rapide ;
- chargement différé des aperçus de lieux avec protection contre l’affichage d’une image obsolète ;
- aucune modification du schéma SQLite ou des formats d’export.

---

# StoryForge 0.26.0 — Vue d’ensemble et export final

## V0.26.0

- ajout d’une vue coordonnée du récit, sans duplication des données ;
- documents, séquences, scènes, cartes, événements, relations et scénario consultables au même endroit ;
- filtres communs et navigation directe vers les outils sources ;
- export final portable regroupant PDF, FDX, Fountain, Markdown, CSV et images ;
- sauvegarde complète réimportable intégrée à chaque archive ;
- correction définitive du chevauchement des entrées latérales actives ;
- textes d’aide des Arcs maintenus sur une ligne ;
- quarante-trois tests automatisés validés.

---

# StoryForge 0.25.0 — Recherche et tags

## V0.25.0

- ajout d’une recherche globale accessible par `Ctrl+K` ;
- navigation directe vers les éléments trouvés ;
- tags transversaux et filtres combinables dans les principaux espaces ;
- gestionnaire de tags avec couleurs, renommage, fusion, compteur d’utilisation et suppression ;
- export/import des tags et de leurs affectations ;
- quarante-deux tests automatisés validés.

---

# StoryForge 0.24.0 — Modèles de fiches

## V0.24.0

- ajout d’une banque de modèles de fiches entièrement locale ;
- construction visuelle par sections et champs dans une interface à trois colonnes ;
- types de champs adaptés à l’écriture : textes, listes, tags, dates, cases, médias et liens ;
- affectation d’un modèle par type de fiche et par projet ;
- ajout des champs de modèle aux Personnages, Lieux, Scènes, Univers et Thème ;
- données existantes préservées lorsque la structure d’un modèle évolue ;
- export/import des modèles et des réponses avec le projet ;
- mise en page du scénario recalculée automatiquement selon la largeur de l’éditeur ;
- quarante-et-un tests automatisés validés.

---

# StoryForge 0.23.2 — SmartType du scénario

## V0.23.2

- suppression de toute création implicite de texte lors des changements de format avec Tab ;
- navigation bornée et entièrement réversible entre les six éléments du scénario ;
- Retour arrière intelligent de Personnage vers Action, puis de Action vers Scène ;
- ajout automatique de `(CONT'D)` lorsqu’un même personnage reprend immédiatement la parole ;
- reconnaissance du personnage indépendante de ses indications `(V.O.)` ou similaires.

---

# StoryForge 0.23.1 — Mise en forme intelligente

## V0.23.1

- retraits visuels professionnels pour les en-têtes, actions, personnages, dialogues, parenthèses et transitions ;
- déplacement immédiat du curseur lors du changement d’élément avec Tab ou Maj+Tab ;
- retour automatique à Action lorsque le nom d’un personnage est entièrement supprimé ;
- retours cohérents entre Dialogue, Personnage et Parenthèse lorsqu’un bloc vide est effacé.

---

# StoryForge 0.23.0 — Écriture du scénario

## V0.23.0

- connexion de l’Éditeur de scripts aux scènes préparées dans Construction ;
- liste unique distinguant scènes écrites et scènes encore à insérer ;
- panneau de contexte avec objectif, personnages, lieu, opposition et états d’entrée/sortie ;
- accès direct aux fiches Personnages et aux scènes de Construction ;
- navigation entre scènes voisines ;
- insertion volontaire d’un en-tête de scène préparée, sans écriture automatique du récit ;
- mode Concentration repliable avec raccourci `Ctrl+Maj+F` ;
- conservation des tabulations intelligentes, versions et exports FDX/PDF.

---

# StoryForge 0.22.1 — Interface harmonisée

## V0.22.1

- correction du badge déformé dans **Guides en cours** ;
- géométrie uniforme des cadres, champs et surfaces de travail ;
- typographie cohérente dans les fiches Personnages et Lieux ;
- hiérarchie à trois niveaux pour les boutons d’action ;
- suppressions définitives présentées comme une variante rouge clairement encadrée ;
- ajout de l’action **Annuler** et retour fiable à la dernière fiche enregistrée ;
- états désactivés cohérents lorsqu’aucune image, référence ou fiche ne peut être retirée.

---

# StoryForge 0.22.0 — Scènes connectées

## V0.22.0

- tableau des scènes enrichi avec lieu, statut et durée ;
- fiche complète de chaque scène en trois onglets ;
- progression de l’entrée à la sortie, avec obstacle, conflit, information et changement ;
- connexions aux personnages, lieux, séquences, chronologie, conflits, thème, motifs, cartes, promesses et moments forts ;
- transformation facultative des séquences en scènes ;
- accès direct à l’Éditeur de scripts ;
- export et import complets des informations et connexions ajoutées ;
- quarante tests automatisés.

---

# StoryForge 0.21.1 — Stabilisation de l’interface

## V0.21.1

- correction du chevauchement vertical de l’onglet actif dans le panneau latéral ;
- nouvelle icône Linux fiable pour **Conflits** ;
- typographie agrandie dans les onglets internes ;
- listes Personnages et Lieux élargies ;
- chargement paresseux et cache des images de Lieux afin de supprimer les décodages répétés ;
- quarante tests automatisés.

---

# StoryForge 0.21.0 — Accroche et promesses

## V0.21.0

- nouvel espace de projet consacré à l’accroche, aux promesses narratives et aux moments forts ;
- suivi de chaque promesse depuis son introduction jusqu’à son accomplissement ;
- moments désirés reliables aux cartes, séquences, scènes, événements et conflits ;
- création directe d’une carte, d’une séquence ou d’une scène depuis un moment fort ;
- vue de contrôle locale, sans IA ni validation automatique ;
- navigation latérale mieux espacée, onglet actif agrandi et colonnes d’icônes parfaitement alignées ;
- export, import et duplication complets ;
- quarante tests automatisés.

---

# StoryForge 0.20.0 — Arcs et transformations

## V0.20.0

- nouvel espace **Arcs** rattaché aux projets ;
- comparaison de tous les personnages dans un tableau synthétique ;
- trajectoire individuelle structurée, synchronisée avec la fiche Personnages ;
- liens explicites avec scènes, cartes de l’histoire, événements et conflits ;
- diagnostic en six repères et sauvegarde automatique ;
- export, import et duplication de toutes les données d’arc ;
- rail de navigation dépliable : icônes et textes en grand, icônes seules en compact ;
- typographie du rail déplié agrandie pour améliorer sa lisibilité ;
- trente-huit tests automatisés.

---

# StoryForge 0.19.2 — Interface Studio

## V0.19.2

- le rail de navigation peut maintenant être déplié ou replié depuis la barre supérieure ;
- `Ctrl+B` commande le même comportement ;
- le choix reste mémorisé au prochain lancement.

# StoryForge 0.19.1 — Interface Studio

## V0.19.1

- nouvelle interface compacte inspirée d’un environnement d’écriture professionnel ;
- barre de projet en haut et navigation par icônes à gauche ;
- palette anthracite avec accent rouge-orangé ;
- panneaux et champs plus sobres, plus droits et mieux alignés ;
- vues Personnages et Lieux recentrées sur leurs trois outils de travail.

# StoryForge 0.19.0 — Conflits connectés

## V0.19.0

- nouvel espace **Conflits** rattaché au projet actif ;
- bibliothèque filtrable de conflits principaux, secondaires, externes, internes, relationnels, sociaux ou liés au monde ;
- fiche unique en quatre onglets : Noyau, Forces, Progression et Connexions ;
- deux camps dotés de leurs propres objectifs, stratégies, avantages, vulnérabilités et pertes possibles ;
- rattachement des personnages et groupes/factions à chaque force ;
- suivi de l’escalade jusqu’au choix difficile, à la confrontation et à ses conséquences ;
- liens avec scènes, cartes de l’histoire, Chronologie et positions thématiques ;
- préremplissage contrôlé depuis les données déjà présentes dans Construction ;
- conservation complète dans les exports, imports et duplications ;
- trente-six tests automatisés.

---

# StoryForge 0.18.0 — Thème et motifs

## V0.18.0

- nouvel espace **Thème** par projet, organisé en Question, Positions, Expression et Motifs ;
- formulation d’une question thématique sans imposer une morale ou une réponse unique ;
- positions principales, opposées et nuancées, reliables aux personnages qui les portent ;
- suivi concret du thème par les décisions, conséquences, conflits et la résolution ;
- motifs classables par type, avec sens possible, apparitions et évolution ;
- connexions des motifs aux lieux, événements de la Chronologie et images existantes ;
- export, import et duplication complets de toutes les données V0.18 ;
- refonte graphique générale maintenue en pause ;
- trente-quatre tests automatisés.

---

# StoryForge 0.16.0 — Bibliothèque de lieux

## V0.16.0

- Personnages est rattaché visuellement à Projets et sa liste adopte la largeur de référence de Lieux (285 px).
- Les champs narratifs de Lieux ont une bordure explicite et toute une ligne de connexion peut cocher ou décocher son élément.
- Le canevas Chronologie conserve désormais ses quatre coins arrondis malgré ses barres de défilement.

- nouvel espace **Lieux** sous Projets, propre à chaque histoire ;
- liste recherchable, filtrable par catégorie et réorganisable ;
- fiche structurée : identité, région, époque, tags, description, fonction narrative, atmosphère, contraintes, évolution et notes ;
- grande couverture visuelle et moodboard reliés à la bibliothèque d’images existante ;
- connexions explicites avec personnages, événements, scènes et images ;
- conservation intégrale des lieux et de leurs connexions dans les exports, imports et duplications ;
- page Personnages rééquilibrée : liste élargie, silhouette plus confortable et fiche moins dominante ;
- carte de l’histoire parcourable par glissement du fond, avec quatre coins réellement arrondis ;
- largeur de la Chronologie recalculée sur son contenu pour supprimer l’extension vide à droite ;
- trente-deux tests automatisés.

---

# StoryForge 0.15.0 — Univers, glossaire et finitions d’édition

## V0.15.0

- nouvel espace **Univers** par projet : Cadre, Règles, Histoire reliée à la Chronologie et Lexique ;
- règles du monde structurées par catégorie, limites, coût, exceptions et conséquence dramatique ;
- connexions facultatives des règles avec personnages, groupes/factions, événements et images ;
- **Guides en cours** déplacé sous Guides d’écriture dans la navigation latérale ;
- lexique propre à chaque projet et glossaire général de soixante termes d’écriture ;
- deux lectures des Templates : traditionnelle et schéma visuel officiel en lecture seule ;
- filtres par recherche et catégorie dans la bibliothèque d’images ;
- silhouettes Femme/Homme, rôles sélectionnables et champs Personnages plus cohérents ;
- liste des personnages légèrement élargie sans déséquilibrer la silhouette et la fiche ;
- carte de l’histoire : contenu encadré et personnages liés par cases à cocher explicites ;
- carte de l’histoire parcourable par glissement du fond, avec quatre coins réellement arrondis ;
- largeur de la Chronologie recalculée sur son contenu pour supprimer l’extension vide à droite après ajout ou suppression ;
- double-clic Chronologie réparé sans reconstruction de la carte sélectionnée ;
- double-clic Projet ouvrant Construction directement sur Prémisse / Concept ;
- éditeurs de la Liste de scènes agrandis et réglage Français/English ajouté ;
- trente-et-un tests automatisés.

---

# StoryForge 0.14.1 — Chronologies libres et idées élargies

## V0.14.1

- plusieurs timelines indépendantes dans un même projet et sur un même canevas ;
- création, renommage, couleur, filtrage et suppression des lignes temporelles ;
- déplacement libre horizontal et vertical du canevas à la souris ;
- édition directe d’un événement par double-clic ;
- formulaire événement entièrement encadré et personnages sélectionnables par cases à cocher ;
- ajout d’un espace « Et si ? » dans chaque idée ;
- intitulés complets des onglets de la fiche Personnages ;
- migration et export/import des timelines ;
- trente tests automatisés.

---

# StoryForge 0.14.0 — Carte des relations

## V0.14.0

- diagramme visuel ouvert depuis le bouton Relations ;
- portraits déplaçables avec sauvegarde automatique des positions ;
- relations directionnelles, nommées et colorées ;
- description, tension, secret et évolution par relation ;
- relations inverses distinctes et lisibles sur deux courbes séparées ;
- cartes indépendantes : générale, libre, famille, travail, début et fin ;
- filtres par personnage ou groupe/faction ;
- canevas quadrillé avec déplacement, zoom et extension automatique ;
- export/import/duplication de toutes les cartes, positions et informations ;
- migration automatique des relations antérieures vers Relations générales ;
- panneau de liste des personnages réduit au profit de la silhouette et de la fiche ;
- vingt-neuf tests automatisés.

---

# StoryForge 0.13.2 — Personnages équilibrés et chronologie mobile

## V0.13.2

- nouvelle page Personnages en trois colonnes équilibrées ;
- liste verticale directement sélectionnable, recherchable, filtrable et scrollable ;
- suppression du bandeau supérieur de navigation devenu redondant ;
- fiche plus étroite avec six onglets compacts ;
- correction des bordures manquantes sur les zones de texte et listes internes ;
- portrait adaptatif toujours affiché entièrement ;
- chronologie navigable par glissement du fond et avec `Maj + molette` ;
- contrôle automatisé de l’équilibre des colonnes et du déplacement horizontal ;
- vingt-sept tests automatisés.

---

# StoryForge 0.13.1 — Ensemble 5 : Personnages approfondis

## V0.13.1

- rôles de personnages structurés sans interdire un rôle personnalisé ;
- groupes et factions créables, modifiables et attribuables à plusieurs personnages ;
- recherche et filtres indépendants par rôle et par groupe dans la bibliothèque compacte ;
- moodboard par personnage avec plusieurs références visuelles et aperçu ;
- conversion d’une référence en portrait par double-clic ;
- champs personnalisés facultatifs organisés en tableau ;
- nouvel onglet **Connexions** réunissant scènes, cartes de l’histoire et événements chronologiques ;
- export, import et duplication des groupes, appartenances, références visuelles et champs libres ;
- migration locale non destructive et vingt-sept tests automatisés.

---

# StoryForge 0.13.0 — Chronologie et nouvelle fiche Personnages

## V0.13.0

- nouvel espace **Chronologie** dans le projet, avec unités Années, Mois, Jours et Heures ;
- événements placés sur des lignes distinctes par catégorie ;
- vues Chronologie complète, Intrigue principale, Backstory et parcours d’un personnage ;
- fiche événement avec repère relatif, libellé libre, lieu, description, conséquence et personnages concernés ;
- filtres par catégorie et zoom horizontal avec `Ctrl + molette` ;
- liste permanente des personnages remplacée par un sélecteur compact et une bibliothèque ouvrable ;
- bibliothèque adaptée aux castings nombreux, avec recherche, filtres de rôles et grille ;
- grande silhouette ou image de référence à gauche et fiche organisée en quatre onglets à droite ;
- fiches enrichies : essentiel, dramaturgie, arc, voix et notes ;
- portraits, nouvelles fiches et chronologie conservés dans les exports, imports et duplications ;
- migration automatique et non destructive des personnages existants ;
- vingt-sept tests automatisés.

---

# StoryForge 0.12.1 — Plan global de l’histoire

## V0.12.1 — Connexions et diagnostic

- synchronisation locale entre le Plan global, le séquencier détaillé et la Liste de scènes ;
- transformation d’un beat en scène et lien facultatif avec une carte de l’histoire ;
- ouverture de la source liée depuis le plan ;
- diagnostic des titres, événements, objectifs, oppositions et conséquences manquants ;
- export/import de la hiérarchie avec remappage de toutes les sources ;
- enregistrement des scènes existantes sans recréer leurs identifiants ni casser leurs connexions ;
- vingt-sept tests automatisés.

## V0.12.0 — Plan global

- nouvelle vue hiérarchique réunissant sections libres, séquences, beats et scènes ;
- aucun découpage en actes imposé ;
- déplacement, changement de niveau, repli/dépli, recherche et zoom ;
- vues compacte et détaillée ;
- séquencier vertical précédent conservé comme vue détaillée spécialisée ;
- migration non destructive des séquences et scènes existantes.

---

# StoryForge 0.11.1 — Guides d’écriture

## V0.11.1

- guides **Renforcer une idée**, **Trouver une fin provisoire** et **Préparer une scène** ;
- projet actif sélectionnable directement depuis le bas de la barre latérale, avec sauvegarde avant changement ;
- prévisualisation avant application au projet ;
- version de la prémisse conservée avant remplacement ;
- fin synchronisée avec la résolution de la Carte de l’histoire ;
- création ou mise à jour d’une scène sans doublon ;
- parcours guidés inclus dans les exports et duplications de projets ;
- vingt-cinq tests automatisés.

## V0.11.0

- nouvel espace **Guides d’écriture** ;
- parcours indépendants avec reprise, archivage et progression propres ;
- migration non destructive du Chemin de la graine existant ;
- niveaux d’aide Découverte, Guidé et Autonome ;
- aucune dépendance à une IA ou à un service payant.

---

# StoryForge 0.10.0 — Création et gestion des projets

## V0.10.0

- création d’un projet avec format cinématographique et durée cible modifiable ;
- démarrage guidé par la graine ou ouverture libre de Construction ;
- recherche, filtres de statut et tris dans la liste des projets ;
- date de dernière modification visible ;
- statuts En cours, En pause et Terminé ;
- duplication profonde d’un projet et de toutes ses données liées ;
- archivage, restauration et suppression définitive protégée ;
- export/import des nouvelles métadonnées ;
- migration non destructive des projets existants ;
- vingt-trois tests automatisés.

---

# StoryForge 0.9.3 — Personnages connectés

## V0.9.3

- relations entre personnages avec nature, description et tension ;
- personnages présents sélectionnables pour chaque scène ;
- personnages liés aux moments de la Carte de l’histoire ;
- connexions conservées dans les exports et imports de projet ;
- migration locale non destructive.

## V0.9.2 — Scènes avancées

- scènes réorganisables verticalement par glisser-déposer ;
- objectif, opposition et changement renseignés scène par scène ;
- durée totale visible en permanence ;
- conversion facultative des blocs du séquencier en scènes ;
- prévention des doublons lors d’une nouvelle conversion.

## V0.9.1 — Éditeur professionnel

- import Final Draft XML avec instantané du texte remplacé ;
- raccourcis `Ctrl+1` à `Ctrl+6`, `Ctrl+S`, Tab et Maj+Tab ;
- page de titre complète ;
- page courante et pagination totale estimées dans l’éditeur ;
- FDX enrichi et PDF avec page de titre, numérotation et coupures améliorées ;
- vingt-et-un tests automatisés.

---

# StoryForge 0.9.1 — États explicites et navigation clavier

## V0.9.1

- bouton **Pas terminé** ajouté au Chemin de la graine ;
- action principale renommée **Terminer et continuer** afin de distinguer sauvegarde et validation ;
- états **Pas fini** et **Terminé** ajoutés à chacune des dix étapes de Construction ;
- coches de Construction basées sur le choix de l’auteur et non plus seulement sur la présence de texte ;
- migration et export/import des états de progression ;
- compteur du Synopsis séparé de sa barre de progression ;
- six questions du Synopsis compactées sans chevauchement ;
- `Tab` et `Maj + Tab` font circuler les types de paragraphes dans l’Éditeur de scripts ;
- passage automatique Personnage → Dialogue après Entrée ;
- type courant affiché au-dessus du scénario ;
- vingt tests automatisés.

---

# StoryForge 0.9.0 — Espaces de projet et éditeur de scripts

## V0.9.0 — Du projet au premier jet

### Organisation

- Projets réduit à une liste unique, large et lisible ;
- Construction replacé comme sous-espace de Projets ;
- sélecteur de projet ajouté dans Construction, Personnages, Images et Éditeur de scripts ;
- nouvelle catégorie Écriture avec Éditeur de scripts et Réécriture ;
- navigation Linux compactée pour rester utilisable en fenêtre de 1120 × 720.

### Idées et références

- grande zone cliquable avec `+` central pour associer une image à une idée ;
- aperçu de l’image dans la fiche ;
- zone interne déroulante en petite fenêtre afin de ne plus comprimer les boutons ;
- nouvelle bibliothèque d’images locale, organisée par projet ;
- nouvelle bibliothèque de personnages avec rôle, fonction, désir, conflit, changement et notes.

### Construction

- explication pratique ajoutée aux étapes Prémisse et Logline ;
- six questions du Synopsis rendues visibles et directement navigables ;
- Treatment précisé sans imposer un format rigide ;
- ajout direct d’un template depuis la Carte de beats ;
- Liste de scènes transformée en tableau Numéro / Titre / Durée ;
- Scénario transformé en synthèse du projet avec accès au nouvel éditeur.

### Éditeur de scripts

- premier jet enregistré automatiquement dans le projet actif ;
- insertion assistée des scènes, actions, personnages, dialogues, parenthèses et transitions ;
- navigation automatique par titres de scènes ;
- compteur de scènes, mots et estimation de pages ;
- création d’instantanés pour la réécriture ;
- export Final Draft XML (`.fdx`) et PDF en Courier ;
- aucun service en ligne ni abonnement nécessaire.

### Templates et données

- catégories renommées selon leur usage ;
- ajout de huit séquences, voyage du héros, Kishōtenketsu, Robert McKee et John Truby ;
- scènes, personnages et images inclus dans les exports/imports de projets ;
- migration non destructive des bases existantes ;
- dix-huit tests automatisés.

---

# StoryForge 0.8.2 — Séquencier visuel et templates

## V0.8.2 — Séquencier visuel

## Séquences

- une séquence par bloc vertical avec titre, fonction, événements et conséquence ;
- réorganisation par glisser-déposer avec une poignée dédiée ;
- ajout, duplication et suppression avec sauvegarde locale ;
- transformation facultative des cartes de l’histoire en premières séquences ;
- ordre causal suivi lorsque les cartes sont reliées ;
- anciennes notes d’outline préservées dans un premier bloc importé ;
- séquencier inclus dans l’export et l’import des projets ;
- mise en page vérifiée dans une fenêtre Linux de 1120 × 720.

## Banque de templates

- nouvelle catégorie Ressources et nouvel onglet Templates ;
- huit modèles couvrant fondations causales, court métrage, structures classiques, modèles alternatifs, genres et beat sheets ;
- fonction, usage conseillé et limite affichés pour chaque modèle ;
- ajout facultatif des repères dans le séquencier du projet actif ;
- aucune structure imposée ni étape considérée comme obligatoire ;
- quatorze tests automatisés.

## V0.8.1 — Graine, projet et Construction

## Organisation

- onglet Apprentissage renommé Chemin de la graine ;
- navigation réordonnée en Commencer, Construire et Progresser ;
- chemin vers la graine séparé des projets déjà créés ;
- graine copiée dans 01 · Prémisse / Concept lors de la création du projet ;
- espace Projets aligné sur les dix étapes exactes de Construction ;
- progression calculée à partir des documents réellement renseignés ;
- ouverture directe de la première étape incomplète ou de n’importe quelle étape choisie ;
- anciens repères du projet conservés dans une fenêtre secondaire ;
- import d’un projet automatiquement activé et replacé dans cette progression.

## V0.8.0 — Synopsis guidé

## Synopsis

- six questions progressives : point de départ, dérèglement, premières conséquences, aggravation, confrontation et résultat ;
- reprise locale de la Carte de l’histoire comme matière première ;
- guide organisé en début, développement et fin sans imposer une structure en actes ;
- une seule question et une grande zone d’écriture à la fois ;
- assemblage en synopsis continu entièrement modifiable ;
- sauvegarde, versions et retour vers les questions ;
- réassemblage avec conservation automatique du texte précédent ;
- export et import des réponses du guide ;
- douze tests automatisés.

## V0.7.7 — Navigation Construction

## Navigation

- numéros 01 à 10 toujours visibles dans l’ordre de travail ;
- validation affichée après le titre sans remplacer son numéro ;
- une carte vide ne valide plus l’étape Carte de l’histoire ;
- suppression de la référence Qt périmée qui empêchait de quitter le canevas après quelques instants ;
- test réel des boutons après la suppression différée de l’ancien éditeur.

## V0.7.6 — Rafraîchissement du canevas

## Affichage Linux

- suppression des fragments de courbes qui pouvaient rester après le déplacement d’une carte ;
- zone de rafraîchissement des pointes de flèche agrandie ;
- canevas entièrement repeint pendant les déplacements afin de nettoyer l’ancien tracé ;
- cartes, liens et positions existants conservés.

## V0.7.5 — Canevas libre

## Espace de travail

- grande réserve vide disponible autour de l’histoire dès l’ouverture ;
- extension du canevas en parcourant ses limites, même lorsqu’aucune carte ne s’y trouve ;
- glissement sécurisé testé avec une carte proche du début du canevas, et non placée artificiellement à droite ;
- données personnelles et positions existantes laissées intactes.

## V0.7.4 — Correction du déplacement des cartes

## Stabilité

- suppression de la récursion Qt qui pouvait faire planter Python pendant l’auto-défilement ;
- déplacement de l’agrandissement et du défilement dans une boucle différée indépendante de la souris ;
- arrêt propre de cette boucle lorsque la carte est relâchée ou lorsque la page change ;
- test automatisé reproduisant plusieurs glisser-déposer au bord du canevas.

## V0.7.3 — Carte visuelle extensible

### Canevas

- agrandissement automatique vers la droite, la gauche, le haut ou le bas ;
- défilement automatique lorsque la carte déplacée atteint un bord visible ;
- déplacement continu sans lâcher la carte pour manipuler un ascenseur ;
- conservation des nouvelles positions dans les données locales.

## V0.7.2 — Construction et carte visuelle

### Construction

- onglet Documents renommé Construction ;
- Carte de l’histoire remplacée par un canevas visuel ;
- cartes déplaçables, colorées par fonction et modifiables au double-clic ;
- création de liens orientés entre deux cartes ;
- suppression locale des cartes et connexions ;
- zoom, centrage et ascenseurs permanents ;
- conversion des neuf réponses causales existantes en cartes reliées ;
- guide causal conservé comme vue optionnelle ;
- export et import des cartes, positions et liens.

## V0.7.1 — Parcours détaillé

### Parcours

- quatre phases sélectionnables dans une navigation compacte ;
- 38 sous-étapes expliquées individuellement ;
- objectif, livrable et critère de passage pour chaque phase ;
- résultat attendu après chaque sous-étape ;
- une seule phase ouverte dans un grand panneau déroulant ;
- sélection mémorisée localement ;
- accès direct à l’espace de travail conseillé ;
- mise en page adaptée aux fenêtres Linux de 1120 × 720.

## V0.7 — Carte de l’histoire

### Carte causale

- neuf étapes conformes à la feuille de route ;
- une question et un grand éditeur déroulant à la fois ;
- situation initiale, dérèglement, objectif, actions, obstacles, conséquences, aggravation, choix, confrontation et résolution ;
- progression enregistrée séparément pour chaque projet ;
- reprise des réponses universelles pertinentes ;
- passage à l’étape suivante seulement après une première réponse ;
- aperçu de la carte en cours ;
- synthèse finale sans structure en actes imposée ;
- ancienne carte préservée automatiquement comme version ;
- export et import des neuf réponses avec le projet.

### Documents

- dix documents guidés, de la prémisse au scénario ;
- une fiche pédagogique compacte par document ;
- grand éditeur déroulant et actions toujours accessibles ;
- navigation précédent / suivant ;
- enregistrement automatique et manuel dans le projet actif ;
- création d’instantanés pour la réécriture ;
- progression visible grâce aux coches dans la liste ;
- reprise des documents existants sans copie ni perte de données ;
- libellés adaptés aux petites fenêtres Linux.

## Parcours complet

- synthèse déroulante à la fin des quatorze questions ;
- création d’un projet en un clic après choix du titre ;
- protagoniste, désir, objectif, opposition, enjeux, changement et fin préremplis ;
- réponses universelles copiées dans le projet ;
- graine enregistrée comme résumé très court ;
- projet nouvellement créé automatiquement activé.

## Projets

- interface divisée en Noyau, Développement et Prochaine action ;
- une seule section visible à la fois ;
- questions ouvertes ajoutées au développement ;
- ouverture directe du projet sélectionné dans l’Atelier ;
- import regroupé avec la liste, export conservé dans les actions du projet.

## Atelier

- document unique au centre de l’écran ;
- grand éditeur avec ascenseur toujours visible ;
- barre d’actions séparée ;
- état du diagnostic local visible dans la fiche du document ;
- libellés raccourcis automatiquement dans les petites fenêtres.

## Compatibilité

- mêmes fichiers sources et même dossier de travail ;
- Linux uniquement ;
- migration additive et anciennes réponses préservées ;
- aucune dépendance OpenAI ;
- douze tests automatisés.
