# Mesures reproductibles

Mesures du 8 septembre 2026, Qt hors écran, fixtures synthétiques uniquement.
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
Lieux 35,99 ms (max 36,82), Personnages 50,08 ms (max 52,23), Vue d’ensemble
17,32 ms (max 22,49). Cette fixture de navigation n’ajoute pas d’images ; le
décodage est mesuré séparément. Pas de promesse de fluidité universelle.

`image_previews.py` borne chaque cache de grands aperçus à 48 Mio de pixels
et les miniatures des lieux à 2 Mio ; ce n’est pas la mémoire totale de Qt.
Éviction LRU, réduction avant décodage lorsque le codec le permet, aucune
modification des originaux. Les invalidations et gardes de génération existantes
restent conservées. Aucun refactoring global de vues n’est justifié par ces mesures.

Tests : `tests/test_image_previews.py` (budget, LRU, original intact et rappel
obsolète), `tests/test_ui_smoke.py` (navigation, images et sauvegarde du scénario
avant changement de projet). Une session Fedora interactive et des photographies
réelles restent utiles pour contrôler le ressenti ; ces tests ne les remplacent pas.
