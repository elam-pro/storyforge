# Mesures reproductibles

Mesures actualisées le 9 septembre 2026, Qt hors écran, fixtures synthétiques uniquement.
Ce sont des indications locales, pas des seuils garantis sur chaque machine.

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python tools/benchmark_previews.py
QT_QPA_PLATFORM=offscreen .venv/bin/python tools/benchmark_navigation.py
```

JPEG 5 000 × 3 500, 15 répétitions : décodage complet puis réduction, médiane
46,35 ms ; réduction demandée au décodeur, 12,43 ms. Cache chaud inférieur à
1 ms. L’image synthétique est uniforme : les photographies complexes et les
formats sans décodage réduit peuvent coûter davantage.

Reconstruction de vues avec 200 personnages et 200 lieux, huit répétitions :
Lieux 55,10 ms (max 57,31), Personnages 50,87 ms (max 51,79), Vue d’ensemble
23,17 ms (max 28,03). Les canevas lourds utilisent les mêmes 200 personnages,
600 événements répartis sur trois timelines et 600 repères géographiques :
Chronologie 19,76 ms (max 27,37), carte de 200 nœuds et 199 relations 50,08 ms
(max 54,42), carte géographique 8,05 ms (max 8,32). Ces mesures couvrent la
construction locale des vues et n’ajoutent pas de portraits ou fonds lourds ;
le décodage est mesuré séparément. Pas de promesse de fluidité universelle.

`image_previews.py` borne chaque cache de grands aperçus à 48 Mio d’octets,
les miniatures des lieux à 2 Mio et celles de la bibliothèque à 8 Mio ; ce
n’est pas la mémoire totale de Qt. La bibliothèque ne charge plus tous les
blobs dans une seule requête, décode directement à 170 × 105 maximum et
réutilise le résultat lors des recherches et changements de filtre.
Les fonds des cartes géographiques sont décodés au plus à 2 400 × 1 600 et
partagent un cache LRU de 32 Mio, vidé lors du changement de projet.
Éviction LRU, réduction avant décodage lorsque le codec le permet, aucune
modification des originaux. Les invalidations et gardes de génération existantes
restent conservées. Aucun refactoring global de vues n’est justifié par ces mesures.

Tests : `tests/test_image_previews.py` (budget, LRU, original intact, rappel
obsolète et miniature de bibliothèque décodée une seule fois),
`tests/test_layout_followup.py` (vues principales à la taille minimale) et
`tests/test_ui_smoke.py` (navigation, images et sauvegarde du scénario avant
changement de projet). Une session Fedora interactive et des photographies
réelles restent utiles pour contrôler le ressenti ; ces tests ne les remplacent pas.
