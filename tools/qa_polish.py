"""Generate isolated UI/PDF samples without reading the user's project database."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from app import StoryForgeWindow
from db import NOW
from report_export import export_report_pdf

qt = QApplication([])
output = Path(tempfile.mkdtemp(prefix="storyforge-qa-"))
window = StoryForgeWindow(output / "qa.db")
window.active_project = window.db.run("INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
                                     (NOW(), "Les Veilleurs", "Idée")).lastrowid
window.resize(1600,1000)
window.show_script_editor()
window.show()
window._insert_script_scene()
qt.processEvents()
window.grab().save(str(output / "editor.png"))
window.db.set_setting("selected_template", "save_the_cat")
window.db.set_setting("template_view_mode", "visual")
window.show_templates()
qt.processEvents()
window.grab().save(str(output / "templates.png"))
export_report_pdf(output / "report.pdf", "# Personnages\n\n## Mina — gardienne du musée\n\n"
                  + "Une décision coûteuse transforme ses relations.\n\n" * 100, "Les Veilleurs")
window.show_genres()
qt.processEvents()
window.grab().save(str(output / "genres.png"))
window.close()
print(output)
