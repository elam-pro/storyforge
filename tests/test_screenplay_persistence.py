from pathlib import Path

from storyforge.db import NOW, Database
from storyforge.screenplay_model import BlockType, ScreenplayDocument


def test_structured_script_survives_storyforge_project_archive(tmp_path: Path) -> None:
    db = Database(tmp_path / "source.db")
    project_id = db.run(
        "INSERT INTO projects(created_at,title,stage) VALUES(?,?,?)",
        (NOW(), "Archive test", "Scénario"),
    ).lastrowid
    db.ensure_doc(project_id, "script", "Scénario")
    document = ScreenplayDocument.from_legacy_text(
        "INT. HALL - JOUR\n\nMINA\nJe reste.",
        project_id=project_id,
    )
    document.set_block_type(2, BlockType.CHARACTER)
    db.save_doc(project_id, "script", document.to_plain_text())
    db.run(
        """INSERT INTO script_meta(project_id,title,document_json,updated_at)
        VALUES(?,?,?,?)""",
        (project_id, "Archive test", document.to_json(), NOW()),
    )

    archive = tmp_path / "archive.storyforge.json"
    db.export_project(project_id, archive)
    imported_id = db.import_project(archive)
    imported_meta = db.one(
        "SELECT document_json FROM script_meta WHERE project_id=?",
        (imported_id,),
    )
    restored = ScreenplayDocument.from_json(imported_meta["document_json"])

    assert restored is not None
    assert restored.document_id == document.document_id
    assert [block.id for block in restored.blocks] == [block.id for block in document.blocks]
    assert restored.elements() == document.elements()
    db.conn.close()

