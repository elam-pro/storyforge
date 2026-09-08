# StoryForge Desktop

Application locale Linux pour apprendre le storytelling en construisant et en écrivant ses histoires. L’apprentissage reste central ; l’atelier sert à appliquer les notions.

## Lancement

Prérequis recommandé : Python 3.11+ avec venv et un environnement graphique Linux.

```bash
./run_linux.sh
```

Le premier lancement crée `.venv` et installe PySide6 (connexion nécessaire à l’installation). Pour réparer ou actualiser l’environnement : `./install_linux.sh`.
Les scripts affichent encore une ancienne version ; la référence est `APP_VERSION` dans [app.py](app.py).

## Données et exports

La base `storyforge.db`, les sauvegardes et les exports sont ignorés par Git. Le manuel cumulatif est généré dans `output/manuals/` à côté de la base ; l’ancien PDF racine reste local et n’est plus suivi. Un commit ne sauvegarde pas les histoires. Ouvrir l’application peut appliquer des migrations : ne pas utiliser les données personnelles pour tester.

- Scénario : Éditeur de scripts → Page de garde → Exporter PDF ou FDX.
- Histoire complète : Projets → Plus… → Exporter l’histoire terminée…, ou Vue d’ensemble.
- L’archive réimportable ne remplace pas une sauvegarde SQLite complète des préférences globales.

## Tests

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
```

Pytest doit être disponible dans l’environnement de développement ; il n’est pas déclaré dans les dépendances runtime. Certains tests PDF nécessitent `pdftotext` (Poppler) et peuvent être ignorés sans cet outil. Les tests doivent utiliser des bases temporaires.

## Documentation ciblée

| Besoin | Source |
| --- | --- |
| Consignes | [AGENTS.md](AGENTS.md) |
| Vision | [Produit](docs/PRODUCT.md) |
| Architecture actuelle | [Architecture](docs/ARCHITECTURE.md) |
| État, code et tests | [Fonctionnalités](docs/FEATURES.md) |
| Décisions | [Décisions](docs/DECISIONS.md) |
| Prochaines étapes | [Roadmap](docs/ROADMAP.md) |
| Mesures de performances | [Fixtures et résultats](docs/PERFORMANCE.md) |
| MCP local optionnel | [Installation et périmètre](docs/MCP.md) |
| Historique | [Release notes](RELEASE_NOTES.md) |

Le code décrit l’implémentation ; les tests les garanties vérifiées ; la roadmap le futur. Les [archives](docs/archive/README.md) ne sont pas des sources actuelles.
