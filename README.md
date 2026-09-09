# StoryForge Desktop

Application locale Linux pour apprendre le storytelling en construisant et en écrivant ses histoires. L’apprentissage reste central ; l’atelier sert à appliquer les notions.

## Installation Linux

Prérequis de construction : Python 3.11+ avec `venv`, une connexion lors de la
première installation et un environnement graphique Linux.

```bash
./install_linux.sh
```

Le script construit un exécutable autonome puis installe StoryForge pour
l’utilisateur courant. L’application est ensuite disponible dans le menu Linux
et avec la commande `storyforge` lorsque `~/.local/bin` est dans le `PATH`.
`./uninstall_linux.sh` retire l’application, le raccourci et l’icône, sans
supprimer les histoires, sauvegardes ou exports.

Pour le développement, `./run_linux.sh` prépare `.venv` au besoin et lance le
package directement. `./scripts/build_linux.sh` reconstruit seulement
`dist/StoryForge`. `./scripts/package_linux_release.sh` crée ensuite une archive
versionnée installable sans environnement de développement, accompagnée de son
checksum SHA-256. La version canonique est dans
[storyforge/version.py](storyforge/version.py).

## Données et exports

Les données sont séparées du code :

- base et sauvegardes : `~/.local/share/storyforge/` ;
- configuration : `~/.config/storyforge/` ;
- cache : `~/.cache/storyforge/` ;
- exports et manuels : `~/Documents/StoryForge/`.

Au premier démarrage, une éventuelle ancienne base placée dans le dépôt est
copiée par l’API SQLite et contrôlée avant utilisation ; la source n’est jamais
écrasée. Un commit ne sauvegarde pas les histoires. Ouvrir l’application peut
appliquer des migrations : ne jamais utiliser les données personnelles pour les
tests.

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
