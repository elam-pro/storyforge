# Migration ponctuelle des libellés — archive non exécutable

Archivée le 8 septembre 2026. Script utilisé pour une migration mécanique passée,
pas une commande de maintenance. Il réécrivait directement app.py lors de son
exécution ou import ; ne pas le réexécuter. Modifier désormais les appels tr ciblés.
Le code original est conservé ci-dessous pour traçabilité, ses chemins sont historiques.

```python
"""One-off mechanical migration of known static UI literals, never user values."""
import ast
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i18n import EN

path = Path(__file__).resolve().parents[1] / "app.py"
source = path.read_text()
lines = source.splitlines(keepends=True)
offsets = [0]
for line in lines:
    offsets.append(offsets[-1] + len(line))
changes = []
allowed = {"make_label", "make_button", "setPlaceholderText", "setToolTip", "QPushButton", "QCheckBox", "setWindowTitle"}
for node in ast.walk(ast.parse(source)):
    if not isinstance(node, ast.Call) or not node.args:
        continue
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
    value = (node.args[2] if name == "_page_header" and len(node.args) > 2 else
             node.args[1] if name == "addTab" and len(node.args) > 1 else node.args[0])
    if name not in allowed | {"addTab", "_page_header"} or not isinstance(value, ast.Constant) or not isinstance(value.value, str):
        continue
    if value.value not in EN and not any(key.upper() == value.value for key in EN):
        continue
    start = offsets[value.lineno-1] + len(lines[value.lineno-1].encode()[:value.col_offset].decode())
    end = offsets[value.end_lineno-1] + len(lines[value.end_lineno-1].encode()[:value.end_col_offset].decode())
    changes.append((start, end))
for start, end in sorted(changes, reverse=True):
    source = source[:start] + "tr(" + source[start:end] + ")" + source[end:]
path.write_text(source)
print(f"Localised {len(changes)} known static UI literals")
```
