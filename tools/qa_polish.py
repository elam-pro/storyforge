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
window.db.set_setting("active_project", window.active_project)
window._update_project_chips()
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
location_ids = []
for position, (name, category) in enumerate((
    ("Citadelle", "Ville"),
    ("Forêt des Veilleurs", "Forêt / nature"),
)):
    location_ids.append(window.db.run(
        """INSERT INTO locations(project_id,position,name,category,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (window.active_project, position, name, category, NOW(), NOW()),
    ).lastrowid)
map_id = window.db.run(
    """INSERT INTO geography_maps(project_id,name,scale_label,created_at,updated_at)
    VALUES(?,?,?,?,?)""",
    (window.active_project, "Royaume des Veilleurs", "Région · 1 case = 10 km", NOW(), NOW()),
).lastrowid
for location_id, label, x, y in (
    (location_ids[0], "Citadelle", 520, 360),
    (location_ids[1], "Forêt des Veilleurs", 1040, 650),
):
    window.db.run(
        """INSERT INTO geography_markers(
        map_id,project_id,location_id,marker_type,label,x,y,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (map_id, window.active_project, location_id, "Lieu", label, x, y, NOW(), NOW()),
    )
window.show_universe()
window.universe_tabs.setCurrentIndex(window.universe_tabs.count() - 1)
window._center_geography_map()
qt.processEvents()
window.grab().save(str(output / "geography.png"))
window.close()
print(output)
