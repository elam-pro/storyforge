import json
import os
import zipfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import StoryForgeWindow, TimelineView
from db import NOW


def test_overview_timeline_uses_readable_relative_units() -> None:
    assert TimelineView.adaptive_relative_label(-6) == "-6 heures"
    assert TimelineView.adaptive_relative_label(-10 * 24) == "-10 jours"
    assert TimelineView.adaptive_relative_label(2 * 30 * 24) == "+2 mois"
    assert TimelineView.adaptive_relative_label(2 * 365 * 24) == "+2 ans"
    assert TimelineView.adaptive_relative_label(-240, "Dix jours avant") == "Dix jours avant"


def test_overview_timeline_displays_the_adaptive_label(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "overview-time.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Repères", "Idée", NOW()),
    ).lastrowid
    track_id = window.db.run(
        """INSERT INTO timeline_tracks(project_id,name,color,position,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Backstory", "#D84A32", 0, NOW(), NOW()),
    ).lastrowid
    window.db.run(
        """INSERT INTO timeline_events(
        project_id,track_id,title,time_hours,display_label,category,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, track_id, "Dix jours plus tôt", -240, "", "Backstory", NOW(), NOW()),
    )
    window.active_project = int(project_id)
    window.db.set_setting("active_project", project_id)
    window.show_story_overview()
    app.processEvents()
    assert window.overview_timeline.topLevelItem(0).text(0) == "-10 jours"
    window.close()


def test_leaving_arcs_ignores_a_deleted_character_selection(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "stale_arc.db")
    project_id = window.db.run(
        "INSERT INTO projects(created_at,title,stage,updated_at) VALUES(?,?,?,?)",
        (NOW(), "Projet sans personnage", "Idée", NOW()),
    ).lastrowid
    window.active_project = int(project_id)
    window.db.set_setting("active_project", project_id)
    window.db.set_setting(f"last_arc_character_{project_id}", 987654)
    window._update_project_chips()

    window.show_arcs()
    app.processEvents()
    assert window.arc_character_id is None
    window.show_home()
    app.processEvents()
    assert window.current_view == "home"
    assert window.db.setting(f"last_arc_character_{project_id}") == "0"
    assert window.db.one(
        "SELECT COUNT(*) FROM character_arcs WHERE project_id=?", (project_id,)
    )[0] == 0
    window.close()


def test_overview_reuses_project_data_and_final_export_is_portable(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = StoryForgeWindow(tmp_path / "v026.db")
    project_id = window.db.run(
        """INSERT INTO projects(created_at,title,stage,project_status,updated_at)
        VALUES(?,?,?,?,?)""",
        (NOW(), "Les Veilleurs", "Premier jet", "completed", NOW()),
    ).lastrowid
    window.active_project = int(project_id)
    window.db.set_setting("active_project", project_id)
    window._update_project_chips()

    window.db.ensure_doc(project_id, "premise", "Prémisse / Concept")
    window.db.save_doc(project_id, "premise", "Une gardienne doit choisir entre le musée et sa sœur.")
    window.db.ensure_doc(project_id, "script", "Scénario")
    window.db.save_doc(
        project_id,
        "script",
        "INT. MUSÉE - NUIT\n\n!Mina déplace le tableau.\n\n@MINA\nNe regarde pas derrière toi.",
    )
    character_a = window.db.run(
        """INSERT INTO characters(project_id,name,role,objective,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "Sauver sa sœur", NOW(), NOW()),
    ).lastrowid
    character_b = window.db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Sarah", "Alliée", NOW(), NOW()),
    ).lastrowid
    window.db.run(
        """INSERT INTO character_relationships(
        project_id,character_a_id,character_b_id,relationship_type,description,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        (project_id, character_a, character_b, "Sœurs", "Une confiance abîmée", NOW(), NOW()),
    )
    sequence_id = window.db.run(
        """INSERT INTO sequence_blocks(project_id,position,title,purpose,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, 0, "Le déplacement", "Déclencher le récit", NOW(), NOW()),
    ).lastrowid
    window.db.run(
        """INSERT INTO scene_rows(
        project_id,position,title,duration,objective,status,source_sequence_id,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, 0, "Le tableau", 2.5, "Cacher son geste", "draft", sequence_id, NOW(), NOW()),
    )
    track_id = window.db.run(
        """INSERT INTO timeline_tracks(project_id,name,color,position,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Intrigue principale", "#D84A32", 0, NOW(), NOW()),
    ).lastrowid
    event_id = window.db.run(
        """INSERT INTO timeline_events(
        project_id,track_id,title,time_hours,display_label,category,description,place,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, track_id, "Le tableau bouge", 0, "Nuit 1", "Intrigue", "Mina agit", "Musée", NOW(), NOW()),
    ).lastrowid
    window.db.run(
        "INSERT INTO timeline_event_characters(event_id,character_id) VALUES(?,?)",
        (event_id, character_a),
    )
    window.db.run(
        """INSERT INTO locations(project_id,position,name,category,description,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, 0, "Musée", "Travail", "Un musée fermé la nuit", NOW(), NOW()),
    )
    map_node_a = window.db.run(
        """INSERT INTO story_map_nodes(
        project_id,title,content,kind,source_step_key,x,y,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, "Le tableau", "Un objet impossible à déplacer", "incident", "seed", 120, 180, NOW(), NOW()),
    ).lastrowid
    map_node_b = window.db.run(
        """INSERT INTO story_map_nodes(
        project_id,title,content,kind,source_step_key,x,y,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, "Le choix", "Mina doit protéger sa sœur", "decision", "decision", 420, 180, NOW(), NOW()),
    ).lastrowid
    window.db.run(
        """INSERT INTO story_map_links(project_id,source_id,target_id,label,created_at)
        VALUES(?,?,?,?,?)""",
        (project_id, map_node_a, map_node_b, "déclenche", NOW()),
    )

    window.show_story_overview()
    app.processEvents()
    assert window.current_view == "overview"
    assert window.overview_tabs.count() == 6
    assert window.overview_documents.topLevelItemCount() == 2
    assert window.overview_plan.topLevelItemCount() == 1
    assert window.overview_cards.count() == 1
    assert window.overview_timeline.topLevelItemCount() == 1
    assert window.overview_relations.topLevelItemCount() == 1
    assert "Mina déplace" in window.overview_script_excerpt.toPlainText()
    window._open_overview_item(window.overview_cards.item(0))
    app.processEvents()
    assert window.current_view == "development"
    assert window.development_doc_type == "scenes"

    destination = tmp_path / "Les_Veilleurs_StoryForge.zip"
    manifest = window._build_final_story_export(project_id, destination)
    assert manifest == {"files": manifest["files"], "characters": 2, "events": 1, "scenes": 1}
    assert manifest["files"] >= 18
    with zipfile.ZipFile(destination) as archive:
        names = set(archive.namelist())
        assert {
            "00_LIRE_MOI.pdf",
            "00_metadata.json",
            "00_manifest.json",
            "01_Scenario/scenario.pdf",
            "01_Scenario/scenario.fdx",
            "01_Scenario/scenario.fountain",
            "01_Scenario/scenario.json",
            "03_Plan/cartes.pdf",
            "03_Plan/cartes.csv",
            "03_Plan/scenes.pdf",
            "04_Chronologie/chronologie.csv",
            "04_Chronologie/chronologie.pdf",
            "05_Personnages/personnages.pdf",
            "05_Personnages/relations.pdf",
            "06_Univers/lieux.pdf",
            "08_Sauvegarde/projet.storyforge.json",
        }.issubset(names)
        metadata = json.loads(archive.read("00_metadata.json").decode("utf-8"))
        assert metadata["format"] == "storyforge-project-metadata-v1"
        assert metadata["project"]["title"] == "Les Veilleurs"
        final_manifest = json.loads(archive.read("00_manifest.json").decode("utf-8"))
        assert final_manifest["format"] == "storyforge-final-v2"
        assert final_manifest["application_version"] == "0.30.3"
        assert final_manifest["counts"]["story_map_nodes"] == 2
        assert final_manifest["counts"]["story_map_links"] == 1
        assert archive.read("03_Plan/cartes.pdf").startswith(b"%PDF")
        assert not any(name.endswith(".md") for name in names)
        scenario = json.loads(archive.read("01_Scenario/scenario.json").decode("utf-8"))
        assert scenario["format"] == "storyforge-screenplay-v1"
        assert scenario["elements"][0] == ["Scene Heading", "INT. MUSÉE - NUIT"]
        exported = json.loads(
            archive.read("08_Sauvegarde/projet.storyforge.json").decode("utf-8")
        )
        assert exported["project"]["title"] == "Les Veilleurs"
        assert exported["characters"][0]["name"] == "Mina"
        assert archive.read("04_Chronologie/chronologie.pdf").startswith(b"%PDF")
    window.close()
