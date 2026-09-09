import sqlite3
from pathlib import Path

from db import NOW, Database


def create_project(db: Database, title: str = "Test") -> int:
    return db.run(
        "INSERT INTO projects(created_at,title,stage,protagonist,objective,opposition,stakes) VALUES(?,?,?,?,?,?,?)",
        (NOW(), title, "Noyau", "Mina", "livrer une lettre", "la ville est fermée", "son frère part à l’aube"),
    ).lastrowid


def test_existing_schema_and_documents_are_preserved(tmp_path: Path) -> None:
    db = Database(tmp_path / "storyforge.db")
    project_id = create_project(db)
    doc = db.ensure_doc(project_id, "synopsis", "Synopsis")
    assert doc["content"] == ""

    db.save_doc(project_id, "synopsis", "Mina traverse la ville.")
    db.snapshot(project_id, "synopsis", "Mina traverse la ville.")

    assert db.one("SELECT content FROM project_docs WHERE project_id=?", (project_id,))[0] == "Mina traverse la ville."
    assert db.one("SELECT COUNT(*) FROM doc_versions WHERE project_id=?", (project_id,))[0] == 1
    db.conn.close()


def test_character_arcs_and_connections_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "arcs.db")
    project_id = create_project(db, "La mue")
    character_id = db.run(
        """INSERT INTO characters(
        project_id,name,role,start_situation,arc,end_situation,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (
            project_id, "Mina", "Protagoniste", "Elle fuit.",
            "Elle accepte de répondre de ses choix.", "Elle reste.", NOW(), NOW(),
        ),
    ).lastrowid
    scene_id = db.run(
        "INSERT INTO scene_rows(project_id,position,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, 0, "Le retour", NOW(), NOW()),
    ).lastrowid
    node_id = db.create_story_map_node(project_id, "Le choix", "Mina revient.", "choice")
    track_id = int(db.ensure_timeline_track(project_id)["id"])
    event_id = db.run(
        "INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, track_id, "Retour de Mina", NOW(), NOW()),
    ).lastrowid
    conflict_id = db.run(
        """INSERT INTO conflicts(project_id,position,title,importance,nature,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, 0, "Fuir ou rester", "main", "internal", NOW(), NOW()),
    ).lastrowid
    arc_id = db.run(
        """INSERT INTO character_arcs(
        project_id,character_id,arc_type,initial_belief,main_trial,pressures,breaking_point,
        decisive_choice,cost,visible_proof,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, character_id, "Transformation positive", "Elle doit agir seule.",
            "Son frère est arrêté.", "Ses refuges disparaissent.", "Il l’a protégée.",
            "Elle revient témoigner.", "Elle perd son anonymat.", "Elle demande de l’aide.",
            "", NOW(), NOW(),
        ),
    ).lastrowid
    db.run("INSERT INTO character_arc_scenes(arc_id,scene_id) VALUES(?,?)", (arc_id, scene_id))
    db.run("INSERT INTO character_arc_story_nodes(arc_id,node_id) VALUES(?,?)", (arc_id, node_id))
    db.run("INSERT INTO character_arc_events(arc_id,event_id) VALUES(?,?)", (arc_id, event_id))
    db.run("INSERT INTO character_arc_conflicts(arc_id,conflict_id) VALUES(?,?)", (arc_id, conflict_id))

    export_path = tmp_path / "arc.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    imported_arc = db.one(
        """SELECT arc.*,character.name,character.start_situation,character.arc transformation,
        character.end_situation FROM character_arcs arc
        JOIN characters character ON character.id=arc.character_id WHERE arc.project_id=?""",
        (imported_id,),
    )
    assert imported_arc["name"] == "Mina"
    assert imported_arc["arc_type"] == "Transformation positive"
    assert imported_arc["decisive_choice"] == "Elle revient témoigner."
    assert imported_arc["transformation"].startswith("Elle accepte")
    for table in (
        "character_arc_scenes", "character_arc_story_nodes",
        "character_arc_events", "character_arc_conflicts",
    ):
        assert db.one(
            f"SELECT COUNT(*) FROM {table} WHERE arc_id=?", (int(imported_arc["id"]),)
        )[0] == 1
    db.conn.close()


def test_hook_promises_and_moments_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "promises.db")
    project_id = create_project(db, "La promesse")
    node_id = db.create_story_map_node(project_id, "La lettre", "Elle reste fermée.", "mystery")
    sequence_id = db.create_sequence_block(project_id, 0, "Le secret")
    scene_id = db.run(
        "INSERT INTO scene_rows(project_id,position,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, 0, "Ouverture de la lettre", NOW(), NOW()),
    ).lastrowid
    track_id = int(db.ensure_timeline_track(project_id)["id"])
    event_id = db.run(
        "INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, track_id, "La lettre arrive", NOW(), NOW()),
    ).lastrowid
    conflict_id = db.run(
        """INSERT INTO conflicts(project_id,position,title,importance,nature,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, 0, "Ouvrir ou livrer", "main", "internal", NOW(), NOW()),
    ).lastrowid
    db.run(
        """INSERT INTO hook_profiles(
        project_id,hook_question,unusual_situation,audience_question,withheld_answer,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        (
            project_id, "Que contient la lettre ?", "Elle arrive dix ans trop tard.",
            "Mina va-t-elle l’ouvrir ?", "Le nom du destinataire.", NOW(), NOW(),
        ),
    )
    promise_id = db.run(
        """INSERT INTO story_promises(
        project_id,position,promise_type,title,description,planted_note,development_note,payoff_note,status,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Mystère", "La lettre sera ouverte", "Son contenu changera Mina.",
            "Le sceau est intact.", "Elle hésite à plusieurs reprises.", "Elle l’ouvre devant son frère.",
            "Accomplie", NOW(), NOW(),
        ),
    ).lastrowid
    db.run("INSERT INTO story_promise_story_nodes(promise_id,node_id) VALUES(?,?)", (promise_id, node_id))
    db.run("INSERT INTO story_promise_scenes(promise_id,scene_id) VALUES(?,?)", (promise_id, scene_id))
    moment_id = db.run(
        """INSERT INTO story_moments(
        project_id,position,moment_type,title,description,narrative_function,placement_note,status,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Révélation", "Mina ouvre la lettre", "Elle lit le nom.",
            "Transformer son objectif.", "À la fin du deuxième mouvement.", "Placée", NOW(), NOW(),
        ),
    ).lastrowid
    for table, column, target_id in (
        ("story_moment_story_nodes", "node_id", node_id),
        ("story_moment_sequences", "sequence_id", sequence_id),
        ("story_moment_scenes", "scene_id", scene_id),
        ("story_moment_events", "event_id", event_id),
        ("story_moment_conflicts", "conflict_id", conflict_id),
    ):
        db.run(f"INSERT INTO {table}(moment_id,{column}) VALUES(?,?)", (moment_id, target_id))

    export_path = tmp_path / "promises.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    imported_hook = db.one("SELECT * FROM hook_profiles WHERE project_id=?", (imported_id,))
    imported_promise = db.one("SELECT * FROM story_promises WHERE project_id=?", (imported_id,))
    imported_moment = db.one("SELECT * FROM story_moments WHERE project_id=?", (imported_id,))
    assert imported_hook["hook_question"] == "Que contient la lettre ?"
    assert imported_promise["status"] == "Accomplie"
    assert imported_moment["moment_type"] == "Révélation"
    for table in ("story_promise_story_nodes", "story_promise_scenes"):
        assert db.one(f"SELECT COUNT(*) FROM {table} WHERE promise_id=?", (imported_promise["id"],))[0] == 1
    for table in (
        "story_moment_story_nodes", "story_moment_sequences", "story_moment_scenes",
        "story_moment_events", "story_moment_conflicts",
    ):
        assert db.one(f"SELECT COUNT(*) FROM {table} WHERE moment_id=?", (imported_moment["id"],))[0] == 1
    db.conn.close()


def test_project_export_import_round_trip(tmp_path: Path) -> None:
    db = Database(tmp_path / "storyforge.db")
    project_id = create_project(db, "La dernière lettre")
    db.run(
        """UPDATE projects SET project_type='film',story_format='short',target_duration=18,
        start_mode='guided',project_status='paused',updated_at=? WHERE id=?""",
        (NOW(), project_id),
    )
    db.ensure_doc(project_id, "summary", "Résumé très court")
    db.save_doc(project_id, "summary", "Une messagère refuse d’abandonner.")
    character_id = db.run(
        "INSERT INTO development_status(project_id,doc_type,status,updated_at) VALUES(?,?,?,?)",
        (project_id, "summary", "draft", NOW()),
    )
    db.save_story_map_answer(project_id, "starting_situation", "Mina travaille de nuit.")
    db.save_synopsis_answer(project_id, "opening_situation", "Mina trie les lettres non distribuées.")
    first_node = db.create_story_map_node(
        project_id,
        "Situation de départ",
        "Mina travaille de nuit.",
        "situation",
        70,
        80,
        "starting_situation",
    )
    second_node = db.create_story_map_node(
        project_id,
        "Événement",
        "Une lettre arrive.",
        "event",
        370,
        80,
        "disrupting_event",
    )
    db.create_story_map_link(project_id, first_node, second_node)
    db.create_sequence_block(
        project_id,
        0,
        "La lettre arrive",
        "Dérégler la nuit de Mina",
        "Mina découvre la lettre.",
        "Elle décide de rejoindre le tribunal.",
        second_node,
    )
    db.run(
        "INSERT INTO scene_rows(project_id,position,title,duration,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        (project_id, 0, "La lettre arrive", 1.5, NOW(), NOW()),
    )
    character_id = db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            "Mina",
            "Protagoniste",
            "Porter la décision",
            "Sauver son frère",
            "Obéir ou agir",
            "Choisir la vérité",
            "Travaille de nuit",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    db.run(
        """UPDATE characters SET age=?,objective=?,start_situation=?,portrait_name=?,portrait_mime=?,portrait_data=?
        WHERE id=?""",
        ("29 ans", "Livrer la lettre", "Mina obéit encore.", "mina.png", "image/png", b"portrait-test", character_id),
    )
    group_id = db.run(
        """INSERT INTO character_groups(
        project_id,name,group_type,description,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?)""",
        (project_id, "Messagers", "Équipe", "Ceux qui transportent les lettres.", "", NOW(), NOW()),
    ).lastrowid
    db.run(
        "INSERT INTO character_group_members(group_id,character_id,role_in_group) VALUES(?,?,?)",
        (group_id, character_id, "Messagère de nuit"),
    )
    db.run(
        """INSERT INTO character_references(
        project_id,character_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, character_id, "Silhouette nocturne", "Costume", "Manteau sombre",
            "mina-reference.png", "image/png", b"reference-test", NOW(), NOW(),
        ),
    )
    db.run(
        "INSERT INTO character_custom_fields(character_id,label,value,position) VALUES(?,?,?,?)",
        (character_id, "Objet fétiche", "Une clé de cuivre", 0),
    )
    form_template_id = db.run(
        """INSERT INTO form_templates(name,target_type,description,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        ("Fiche sensorielle", "character", "Compléments utiles", NOW(), NOW()),
    ).lastrowid
    form_section_id = db.run(
        "INSERT INTO form_template_sections(template_id,title,position) VALUES(?,?,?)",
        (form_template_id, "Perception", 0),
    ).lastrowid
    form_field_id = db.run(
        """INSERT INTO form_template_fields(
        template_id,section_id,label,field_type,options_json,help_text,
        default_value,required,position) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            form_template_id,
            form_section_id,
            "Odeur associée",
            "text_short",
            "[]",
            "Un repère sensoriel",
            "",
            0,
            0,
        ),
    ).lastrowid
    db.run(
        "INSERT INTO project_form_templates(project_id,target_type,template_id) VALUES(?,?,?)",
        (project_id, "character", form_template_id),
    )
    db.run(
        """INSERT INTO form_field_values(
        project_id,target_type,entity_id,field_id,value_text,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "character", character_id, form_field_id, "Papier mouillé", NOW()),
    )
    main_timeline = db.ensure_timeline_track(project_id, "Intrigue principale", "#3D8EF7")
    backstory_timeline = db.ensure_timeline_track(project_id, "Backstory", "#9B6BDE")
    timeline_event_id = db.run(
        """INSERT INTO timeline_events(
        project_id,track_id,title,time_hours,display_label,category,description,place,consequence,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, int(backstory_timeline["id"]), "Disparition du frère", -48, "Deux jours avant", "Backstory",
            "Le frère de Mina disparaît.", "Quartier nord", "Mina accepte la lettre.", NOW(), NOW(),
        ),
    ).lastrowid
    db.run(
        "INSERT INTO timeline_event_characters(event_id,character_id) VALUES(?,?)",
        (timeline_event_id, character_id),
    )
    db.run(
        """INSERT INTO image_library(
        project_id,title,category,notes,file_name,mime_type,image_data,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            "Ville fermée",
            "Lieu / décor",
            "Référence nocturne",
            "ville.png",
            "image/png",
            b"image-test",
            NOW(),
            NOW(),
        ),
    )
    export_path = tmp_path / "project.storyforge.json"

    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)

    imported = db.one("SELECT * FROM projects WHERE id=?", (imported_id,))
    imported_doc = db.one("SELECT content FROM project_docs WHERE project_id=? AND doc_type='summary'", (imported_id,))
    imported_map = db.one(
        "SELECT answer FROM story_map_answers WHERE project_id=? AND step_key='starting_situation'",
        (imported_id,),
    )
    imported_synopsis_answer = db.one(
        "SELECT answer FROM synopsis_answers WHERE project_id=? AND step_key='opening_situation'",
        (imported_id,),
    )
    assert imported["title"] == "La dernière lettre"
    assert imported["project_type"] == "film"
    assert imported["story_format"] == "short"
    assert imported["target_duration"] == 18
    assert imported["start_mode"] == "guided"
    assert imported["project_status"] == "paused"
    assert imported_doc["content"] == "Une messagère refuse d’abandonner."
    assert db.one(
        "SELECT status FROM development_status WHERE project_id=? AND doc_type='summary'",
        (imported_id,),
    )[0] == "draft"
    assert imported_map["answer"] == "Mina travaille de nuit."
    assert imported_synopsis_answer["answer"] == "Mina trie les lettres non distribuées."
    assert db.one("SELECT COUNT(*) FROM story_map_nodes WHERE project_id=?", (imported_id,))[0] == 2
    imported_link = db.one(
        """SELECT source.title source_title,target.title target_title
        FROM story_map_links link
        JOIN story_map_nodes source ON source.id=link.source_id
        JOIN story_map_nodes target ON target.id=link.target_id
        WHERE link.project_id=?""",
        (imported_id,),
    )
    assert imported_link["source_title"] == "Situation de départ"
    assert imported_link["target_title"] == "Événement"
    imported_sequence = db.one(
        """SELECT block.title,block.purpose,node.title source_title
        FROM sequence_blocks block
        LEFT JOIN story_map_nodes node ON node.id=block.source_node_id
        WHERE block.project_id=?""",
        (imported_id,),
    )
    assert imported_sequence["title"] == "La lettre arrive"
    assert imported_sequence["purpose"] == "Dérégler la nuit de Mina"
    assert imported_sequence["source_title"] == "Événement"
    assert db.one(
        "SELECT title,duration FROM scene_rows WHERE project_id=?",
        (imported_id,),
    )["duration"] == 1.5
    imported_character = db.one(
        "SELECT id,name,role,objective,portrait_data FROM characters WHERE project_id=?",
        (imported_id,),
    )
    assert imported_character["name"] == "Mina"
    assert imported_character["objective"] == "Livrer la lettre"
    assert bytes(imported_character["portrait_data"]) == b"portrait-test"
    imported_group = db.one(
        "SELECT id,name,group_type FROM character_groups WHERE project_id=?",
        (imported_id,),
    )
    assert imported_group["name"] == "Messagers"
    assert imported_group["group_type"] == "Équipe"
    assert db.one(
        """SELECT role_in_group FROM character_group_members
        WHERE group_id=? AND character_id=?""",
        (imported_group["id"], imported_character["id"]),
    )[0] == "Messagère de nuit"
    imported_reference = db.one(
        "SELECT title,image_data FROM character_references WHERE project_id=?",
        (imported_id,),
    )
    assert imported_reference["title"] == "Silhouette nocturne"
    assert bytes(imported_reference["image_data"]) == b"reference-test"
    assert db.one(
        "SELECT label,value FROM character_custom_fields WHERE character_id=?",
        (imported_character["id"],),
    )["value"] == "Une clé de cuivre"
    imported_form_template = db.one(
        """SELECT template.id,template.name FROM form_templates template
        JOIN project_form_templates assignment ON assignment.template_id=template.id
        WHERE assignment.project_id=? AND assignment.target_type='character'""",
        (imported_id,),
    )
    assert imported_form_template["name"] == "Fiche sensorielle"
    imported_form_value = db.one(
        """SELECT value.value_text FROM form_field_values value
        JOIN form_template_fields field ON field.id=value.field_id
        WHERE value.project_id=? AND value.entity_id=? AND field.label=?""",
        (imported_id, imported_character["id"], "Odeur associée"),
    )
    assert imported_form_value["value_text"] == "Papier mouillé"
    assert main_timeline["name"] == "Intrigue principale"
    imported_timeline = db.one(
        """SELECT event.id,event.title,event.time_hours,event.category,track.name track_name
        FROM timeline_events event JOIN timeline_tracks track ON track.id=event.track_id
        WHERE event.project_id=?""",
        (imported_id,),
    )
    assert imported_timeline["title"] == "Disparition du frère"
    assert imported_timeline["time_hours"] == -48
    assert imported_timeline["track_name"] == "Backstory"
    assert db.one(
        "SELECT COUNT(*) FROM timeline_tracks WHERE project_id=?",
        (imported_id,),
    )[0] == 2
    assert db.one(
        """SELECT COUNT(*) FROM timeline_event_characters
        WHERE event_id=? AND character_id=?""",
        (imported_timeline["id"], imported_character["id"]),
    )[0] == 1
    imported_image = db.one(
        "SELECT title,image_data FROM image_library WHERE project_id=?",
        (imported_id,),
    )
    assert imported_image["title"] == "Ville fermée"
    assert bytes(imported_image["image_data"]) == b"image-test"
    db.conn.close()


def test_unassigned_timeline_events_migrate_to_named_tracks(tmp_path: Path) -> None:
    path = tmp_path / "legacy-timeline.db"
    db = Database(path)
    project_id = create_project(db, "Chronologie ancienne")
    event_id = db.run(
        """INSERT INTO timeline_events(
        project_id,title,time_hours,display_label,category,description,place,consequence,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, "Une ancienne guerre", -24000, "Avant", "Monde",
            "La frontière tombe.", "Nord", "Les familles fuient.", NOW(), NOW(),
        ),
    ).lastrowid
    db.conn.close()

    migrated = Database(path)
    row = migrated.one(
        """SELECT event.track_id,track.name FROM timeline_events event
        JOIN timeline_tracks track ON track.id=event.track_id WHERE event.id=?""",
        (event_id,),
    )
    assert row["track_id"]
    assert row["name"] == "Monde"
    migrated.conn.close()


def test_learning_loop_mastery_and_backup(tmp_path: Path) -> None:
    db = Database(tmp_path / "storyforge.db")
    db.save_learning_work(
        "session01",
        0,
        "idee",
        "Premier essai",
        "Un problème principal",
        "Version réécrite",
        "Une idée fait naître une question.",
        "fragile",
        "terminé",
    )
    db.set_concept_mastery("idee", "Idée", "fragile", "Version réécrite")
    backup = tmp_path / "copies" / "backup.db"
    db.backup_to(backup)

    restored = Database(backup)
    assert restored.one("SELECT revision FROM learning_work WHERE step_index=0")[0] == "Version réécrite"
    assert restored.one("SELECT status FROM concept_mastery WHERE concept_key='idee'")[0] == "fragile"
    restored.conn.close()
    db.conn.close()


def test_advanced_scenes_characters_and_title_page_round_trip(tmp_path: Path) -> None:
    db = Database(tmp_path / "connected.db")
    project_id = create_project(db, "Les deux portes")
    first_character = db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "Décider", "Sortir", "Doute", "Agir", "", NOW(), NOW()),
    ).lastrowid
    second_character = db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Noé", "Allié", "Résister", "Rester", "Peur", "Avouer", "", NOW(), NOW()),
    ).lastrowid
    relationship_map_id = int(db.ensure_relationship_map(project_id)["id"])
    db.run(
        "INSERT INTO relationship_map_nodes(map_id,character_id,x,y) VALUES(?,?,?,?)",
        (relationship_map_id, first_character, 120, 180),
    )
    db.run(
        "INSERT INTO relationship_map_nodes(map_id,character_id,x,y) VALUES(?,?,?,?)",
        (relationship_map_id, second_character, 540, 260),
    )
    node_id = db.create_story_map_node(project_id, "La porte s’ouvre", "Mina hésite.", "event")
    sequence_id = db.create_sequence_block(project_id, 0, "Le choix", "Forcer une décision", "Deux portes", "Mina choisit")
    timeline_id = int(db.ensure_timeline_track(project_id, "Intrigue principale", "#3D8EF7")["id"])
    event_id = db.run(
        """INSERT INTO timeline_events(
        project_id,track_id,title,time_hours,display_label,category,description,place,consequence,
        created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            timeline_id,
            "La serrure cède",
            2,
            "Jour 1",
            "Intrigue principale",
            "La porte réagit au choix de Mina.",
            "Couloir",
            "Une seule issue reste ouverte.",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    theme_position_id = db.run(
        """INSERT INTO theme_positions(
        project_id,position,position_type,label,stance,nuance,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (
            project_id,
            0,
            "principale",
            "Choisir engage",
            "Toute décision transforme celui qui la prend.",
            "Ne pas choisir est encore un choix.",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    motif_id = db.run(
        """INSERT INTO theme_motifs(
        project_id,position,name,motif_type,meaning,appearances,evolution,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id,
            0,
            "Les deux poignées",
            "Objet",
            "Le prix du choix",
            "Avant chaque décision",
            "L’une des poignées disparaît",
            NOW(),
            NOW(),
        ),
    ).lastrowid
    scene_id = db.run(
        """INSERT INTO scene_rows(
        project_id,position,title,duration,objective,opposition,change_note,status,moment_label,
        driver_character_id,character_objective,conflict_note,information_revealed,
        entry_state,exit_state,notes,source_sequence_id,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Devant les portes", 2.5, "Choisir", "Noé refuse", "Mina agit",
            "draft", "Jour 1 · matin", first_character, "Convaincre Noé de la suivre",
            "Deux volontés deviennent incompatibles", "Noé connaît la sortie",
            "Les deux portes sont encore accessibles", "Une porte se condamne",
            "Garder le choix visible.", sequence_id, NOW(), NOW(),
        ),
    ).lastrowid
    db.run("INSERT INTO scene_characters(scene_id,character_id) VALUES(?,?)", (scene_id, first_character))
    db.run("INSERT INTO scene_events(scene_id,event_id) VALUES(?,?)", (scene_id, event_id))
    db.run("INSERT INTO scene_story_nodes(scene_id,node_id) VALUES(?,?)", (scene_id, node_id))
    db.run(
        "INSERT INTO scene_theme_positions(scene_id,position_id) VALUES(?,?)",
        (scene_id, theme_position_id),
    )
    db.run("INSERT INTO scene_theme_motifs(scene_id,motif_id) VALUES(?,?)", (scene_id, motif_id))
    db.run("INSERT INTO story_map_node_characters(node_id,character_id) VALUES(?,?)", (node_id, second_character))
    db.run(
        """INSERT INTO character_relationships(
        project_id,map_id,character_a_id,character_b_id,relationship_type,description,tension,
        secret,evolution,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, relationship_map_id, first_character, second_character, "Amitié",
            "Ils se protègent", "Ils veulent deux issues", "Noé connaît la sortie",
            "L’amitié devient une rupture", "#3C93FF", NOW(), NOW(),
        ),
    )
    ending_map_id = db.run(
        """INSERT INTO relationship_maps(project_id,name,map_type,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Fin de l’histoire", "end", NOW(), NOW()),
    ).lastrowid
    db.run(
        "INSERT INTO relationship_map_nodes(map_id,character_id,x,y) VALUES(?,?,?,?)",
        (ending_map_id, first_character, 220, 160),
    )
    db.run(
        "INSERT INTO relationship_map_nodes(map_id,character_id,x,y) VALUES(?,?,?,?)",
        (ending_map_id, second_character, 680, 160),
    )
    db.run(
        """INSERT INTO character_relationships(
        project_id,map_id,character_a_id,character_b_id,relationship_type,description,tension,
        secret,evolution,color,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, ending_map_id, second_character, first_character, "Méfiance",
            "Noé doute désormais de Mina", "Une vérité les sépare", "", "Ils s’éloignent",
            "#C49A34", NOW(), NOW(),
        ),
    )
    db.run(
        """INSERT INTO script_meta(
        project_id,title,author,contact,draft_date,based_on,copyright_notice,
        include_title_page,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            project_id, "Les deux portes", "Camille", "camille@example.test",
            "Version 3", "Une histoire originale", "Copyright 2026 Camille",
            1, NOW(),
        ),
    )
    path = tmp_path / "connected.storyforge.json"
    db.export_project(project_id, path)
    imported_id = db.import_project(path)

    imported_scene = db.one("SELECT * FROM scene_rows WHERE project_id=?", (imported_id,))
    assert imported_scene["objective"] == "Choisir"
    assert imported_scene["opposition"] == "Noé refuse"
    assert imported_scene["change_note"] == "Mina agit"
    assert imported_scene["status"] == "draft"
    assert imported_scene["moment_label"] == "Jour 1 · matin"
    assert imported_scene["driver_character_id"] > 0
    assert imported_scene["character_objective"] == "Convaincre Noé de la suivre"
    assert imported_scene["conflict_note"].startswith("Deux volontés")
    assert imported_scene["information_revealed"] == "Noé connaît la sortie"
    assert imported_scene["entry_state"].startswith("Les deux portes")
    assert imported_scene["exit_state"] == "Une porte se condamne"
    assert imported_scene["notes"] == "Garder le choix visible."
    assert imported_scene["source_sequence_id"] > 0
    assert db.one("SELECT COUNT(*) FROM scene_characters WHERE scene_id=?", (imported_scene["id"],))[0] == 1
    for table in (
        "scene_events",
        "scene_story_nodes",
        "scene_theme_positions",
        "scene_theme_motifs",
    ):
        assert db.one(f"SELECT COUNT(*) FROM {table} WHERE scene_id=?", (imported_scene["id"],))[0] == 1
    imported_node = db.one("SELECT id FROM story_map_nodes WHERE project_id=?", (imported_id,))
    assert db.one("SELECT COUNT(*) FROM story_map_node_characters WHERE node_id=?", (imported_node["id"],))[0] == 1
    imported_relationship_map = db.one(
        "SELECT id,name FROM relationship_maps WHERE project_id=? AND name='Relations générales'",
        (imported_id,),
    )
    assert imported_relationship_map["name"] == "Relations générales"
    assert db.one(
        "SELECT COUNT(*) FROM relationship_maps WHERE project_id=?",
        (imported_id,),
    )[0] == 2
    imported_positions = db.q(
        "SELECT x,y FROM relationship_map_nodes WHERE map_id=? ORDER BY x",
        (imported_relationship_map["id"],),
    )
    assert [(row["x"], row["y"]) for row in imported_positions] == [(120, 180), (540, 260)]
    relation = db.one(
        """SELECT relationship_type,tension,secret,evolution,color,map_id
        FROM character_relationships WHERE project_id=? AND relationship_type='Amitié'""",
        (imported_id,),
    )
    assert relation["relationship_type"] == "Amitié"
    assert relation["tension"] == "Ils veulent deux issues"
    assert relation["secret"] == "Noé connaît la sortie"
    assert relation["evolution"] == "L’amitié devient une rupture"
    assert relation["color"] == "#3C93FF"
    assert relation["map_id"] == imported_relationship_map["id"]
    assert db.one(
        "SELECT COUNT(*) FROM character_relationships WHERE project_id=?",
        (imported_id,),
    )[0] == 2
    imported_ending_map = db.one(
        "SELECT id FROM relationship_maps WHERE project_id=? AND name='Fin de l’histoire'",
        (imported_id,),
    )
    assert db.one(
        "SELECT COUNT(*) FROM relationship_map_nodes WHERE map_id=?",
        (imported_ending_map["id"],),
    )[0] == 2
    meta = db.one("SELECT * FROM script_meta WHERE project_id=?", (imported_id,))
    assert meta["author"] == "Camille"
    assert meta["draft_date"] == "Version 3"
    assert meta["based_on"] == "Une histoire originale"
    assert meta["copyright_notice"] == "Copyright 2026 Camille"
    assert meta["include_title_page"] == 1
    db.conn.close()


def test_unassigned_relationships_migrate_to_a_general_map(tmp_path: Path) -> None:
    path = tmp_path / "legacy-relations.db"
    db = Database(path)
    project_id = create_project(db, "Relations anciennes")
    first_character = db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "", "", "", "", "", NOW(), NOW()),
    ).lastrowid
    second_character = db.run(
        """INSERT INTO characters(
        project_id,name,role,story_function,desire,conflict,arc,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Sarah", "Allié", "", "", "", "", "", NOW(), NOW()),
    ).lastrowid
    db.run(
        """INSERT INTO character_relationships(
        project_id,character_a_id,character_b_id,relationship_type,description,tension,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, first_character, second_character, "Respect", "", "", NOW(), NOW()),
    )
    db.conn.close()

    migrated = Database(path)
    relationship_map = migrated.one(
        "SELECT id,name FROM relationship_maps WHERE project_id=?",
        (project_id,),
    )
    assert relationship_map["name"] == "Relations générales"
    assert migrated.one(
        "SELECT map_id FROM character_relationships WHERE project_id=?",
        (project_id,),
    )[0] == relationship_map["id"]
    migrated.conn.close()


def test_global_outline_round_trip_preserves_hierarchy_and_source_links(tmp_path: Path) -> None:
    db = Database(tmp_path / "outline.db")
    project_id = create_project(db, "Le plan")
    node_id = db.create_story_map_node(project_id, "Le signal", "Une lumière s’allume.", "event")
    sequence_id = db.create_sequence_block(
        project_id,
        0,
        "Le signal",
        "Lancer la recherche",
        "Mina voit la lumière.",
        "Elle quitte la maison.",
        node_id,
    )
    scene_id = db.run(
        """INSERT INTO scene_rows(
        project_id,position,title,duration,objective,opposition,change_note,source_sequence_id,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "La lumière", 1.5, "Comprendre", "La porte est fermée",
            "Mina sort", sequence_id, NOW(), NOW(),
        ),
    ).lastrowid
    section_id = db.create_outline_item(project_id, 0, "section", "Départ")
    outline_sequence_id = db.create_outline_item(
        project_id,
        0,
        "sequence",
        "Le signal",
        "Mina voit la lumière.",
        "Lancer la recherche",
        "Elle quitte la maison.",
        parent_id=section_id,
        source_sequence_id=sequence_id,
        source_node_id=node_id,
    )
    db.create_outline_item(
        project_id,
        0,
        "scene",
        "La lumière",
        "La porte est fermée",
        "Comprendre",
        "Mina sort",
        parent_id=outline_sequence_id,
        source_scene_id=scene_id,
    )

    path = tmp_path / "outline.storyforge.json"
    db.export_project(project_id, path)
    imported_id = db.import_project(path)
    imported = db.q(
        "SELECT * FROM outline_items WHERE project_id=? ORDER BY id",
        (imported_id,),
    )
    assert len(imported) == 3
    section, sequence, scene = imported
    assert sequence["parent_id"] == section["id"]
    assert scene["parent_id"] == sequence["id"]
    assert sequence["source_sequence_id"] > 0
    assert sequence["source_node_id"] > 0
    assert scene["source_scene_id"] > 0
    assert db.one(
        "SELECT source_sequence_id FROM scene_rows WHERE id=?",
        (scene["source_scene_id"],),
    )[0] == sequence["source_sequence_id"]
    db.conn.close()


def test_v04_learning_answer_becomes_v05_first_draft(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    legacy = sqlite3.connect(path)
    legacy.execute("CREATE TABLE learning_answers(id INTEGER PRIMARY KEY, session_key TEXT, step_index INTEGER, answer TEXT, updated_at TEXT)")
    legacy.execute("CREATE UNIQUE INDEX legacy_answer ON learning_answers(session_key, step_index)")
    legacy.execute("INSERT INTO learning_answers(session_key,step_index,answer,updated_at) VALUES('session01',0,'Ancienne réponse','2026-01-01')")
    legacy.commit()
    legacy.close()

    db = Database(path)
    work = db.ensure_learning_work("session01", 0, "idee")
    assert work["draft"] == "Ancienne réponse"
    assert work["revision"] == ""
    db.conn.close()


def test_existing_ideas_gain_a_non_destructive_type_filter(tmp_path: Path) -> None:
    path = tmp_path / "legacy-ideas.db"
    legacy = sqlite3.connect(path)
    legacy.execute(
        """CREATE TABLE ideas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL,title TEXT NOT NULL,
        seed TEXT NOT NULL DEFAULT '',attraction TEXT NOT NULL DEFAULT '',
        potential TEXT NOT NULL DEFAULT 'inconnu',status TEXT NOT NULL DEFAULT 'brute')"""
    )
    legacy.execute(
        "INSERT INTO ideas(created_at,title,seed,attraction,potential,status) VALUES(?,?,?,?,?,?)",
        ("2026-01-01", "Idée ancienne", "Une image.", "Son étrangeté.", "court", "retenue"),
    )
    legacy.commit()
    legacy.close()

    db = Database(path)
    migrated = db.one(
        "SELECT title,seed,idea_type,attachment_name,attachment_mime,attachment_data FROM ideas"
    )
    assert migrated["title"] == "Idée ancienne"
    assert migrated["seed"] == "Une image."
    assert migrated["idea_type"] == "unclassified"
    assert migrated["attachment_name"] == ""
    assert migrated["attachment_mime"] == ""
    assert migrated["attachment_data"] is None
    db.conn.close()


def test_new_document_is_not_completed_just_because_it_has_text(tmp_path: Path) -> None:
    path = tmp_path / "explicit-status.db"
    db = Database(path)
    project_id = create_project(db, "Brouillon explicite")
    db.ensure_doc(project_id, "logline", "Logline")
    db.save_doc(project_id, "logline", "Une phrase existe, mais elle reste à reprendre.")
    db.conn.close()

    reopened = Database(path)
    assert reopened.one(
        "SELECT status FROM development_status WHERE project_id=? AND doc_type='logline'",
        (project_id,),
    ) is None
    reopened.conn.close()


def test_v015_world_and_character_gender_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "world.db")
    project_id = create_project(db, "La cité de verre")
    db.run(
        """INSERT INTO world_profiles(
        project_id,epoch,places,society,culture,worldview,originality,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, "Après la crue", "La tour", "Conseil fermé", "Rituels d'eau", "Le verre se souvient", "Mémoire minérale", NOW(), NOW()),
    )
    rule_id = db.run(
        """INSERT INTO world_rules(
        project_id,category,title,rule_text,scope,limitation,cost,exceptions,consequence,status,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (project_id, "Magie et surnaturel", "Le verre retient une voix", "Une seule voix par objet", "Verre taillé", "Pas d'image", "Le souvenir s'efface", "Verre royal", "Un témoin perd une preuve", "established", NOW(), NOW()),
    ).lastrowid
    db.run(
        """INSERT INTO world_terms(project_id,category,term,definition,usage,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        (project_id, "Institution", "Conseil", "Pouvoir de la tour", "Interdit les archives", NOW(), NOW()),
    )
    character_id = db.run(
        """INSERT INTO characters(project_id,name,role,gender,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", "female", NOW(), NOW()),
    ).lastrowid
    group_id = db.run(
        """INSERT INTO character_groups(project_id,name,group_type,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Conseil", "Faction", NOW(), NOW()),
    ).lastrowid
    track_id = int(db.ensure_timeline_track(project_id, "Monde")["id"])
    event_id = db.run(
        """INSERT INTO timeline_events(project_id,track_id,title,category,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, track_id, "La grande crue", "Monde", NOW(), NOW()),
    ).lastrowid
    image_id = db.run(
        """INSERT INTO image_library(
        project_id,title,category,image_data,created_at,updated_at
        ) VALUES(?,?,?,?,?,?)""",
        (project_id, "Tour", "Lieu / décor", b"image", NOW(), NOW()),
    ).lastrowid
    for table, column, target_id in (
        ("world_rule_characters", "character_id", character_id),
        ("world_rule_groups", "group_id", group_id),
        ("world_rule_events", "event_id", event_id),
        ("world_rule_images", "image_id", image_id),
    ):
        db.run(f"INSERT INTO {table}(rule_id,{column}) VALUES(?,?)", (rule_id, target_id))
    export_path = tmp_path / "world.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    assert db.one("SELECT epoch FROM world_profiles WHERE project_id=?", (imported_id,))[0] == "Après la crue"
    assert db.one("SELECT title FROM world_rules WHERE project_id=?", (imported_id,))[0] == "Le verre retient une voix"
    assert db.one("SELECT term FROM world_terms WHERE project_id=?", (imported_id,))[0] == "Conseil"
    assert db.one("SELECT gender FROM characters WHERE project_id=?", (imported_id,))[0] == "female"
    imported_rule_id = db.one("SELECT id FROM world_rules WHERE project_id=?", (imported_id,))[0]
    for table in ("world_rule_characters", "world_rule_groups", "world_rule_events", "world_rule_images"):
        assert db.one(f"SELECT COUNT(*) FROM {table} WHERE rule_id=?", (imported_rule_id,))[0] == 1
    db.conn.close()


def test_v016_locations_and_connections_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "locations.db")
    project_id = create_project(db, "La maison ouverte")
    character_id = db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    scene_id = db.run(
        """INSERT INTO scene_rows(project_id,position,title,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, 0, "La fenêtre s’ouvre", NOW(), NOW()),
    ).lastrowid
    track_id = int(db.ensure_timeline_track(project_id, "Intrigue principale")["id"])
    event_id = db.run(
        """INSERT INTO timeline_events(project_id,track_id,title,place,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, track_id, "Retour à la maison", "Maison de Mina", NOW(), NOW()),
    ).lastrowid
    image_id = db.run(
        """INSERT INTO image_library(project_id,title,category,image_data,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Façade", "Lieu / décor", b"location-image", NOW(), NOW()),
    ).lastrowid
    location_id = db.run(
        """INSERT INTO locations(
        project_id,position,name,category,region,epoch,tags,description,narrative_function,
        atmosphere,constraints_note,evolution,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Maison de Mina", "Maison / intérieur", "Quartier nord", "Présent",
            "départ, secret", "Une maison trop silencieuse.", "Lieu de départ et de révélation.",
            "Fausse sécurité", "Une seule sortie", "Elle devient une prison", "Conserver la fenêtre",
            NOW(), NOW(),
        ),
    ).lastrowid
    db.run("INSERT INTO location_characters(location_id,character_id) VALUES(?,?)", (location_id, character_id))
    db.run("INSERT INTO location_events(location_id,event_id) VALUES(?,?)", (location_id, event_id))
    db.run("INSERT INTO location_scenes(location_id,scene_id) VALUES(?,?)", (location_id, scene_id))
    db.run(
        "INSERT INTO location_images(location_id,image_id,position,is_primary) VALUES(?,?,?,?)",
        (location_id, image_id, 0, 1),
    )

    export_path = tmp_path / "locations.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    imported_location = db.one("SELECT * FROM locations WHERE project_id=?", (imported_id,))
    assert imported_location["name"] == "Maison de Mina"
    assert imported_location["narrative_function"] == "Lieu de départ et de révélation."
    assert imported_location["constraints_note"] == "Une seule sortie"
    for table in ("location_characters", "location_events", "location_scenes", "location_images"):
        assert db.one(
            f"SELECT COUNT(*) FROM {table} WHERE location_id=?",
            (int(imported_location["id"]),),
        )[0] == 1
    assert db.one(
        "SELECT is_primary FROM location_images WHERE location_id=?",
        (int(imported_location["id"]),),
    )[0] == 1
    db.conn.close()


def test_geography_maps_reuse_locations_images_and_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "geography.db")
    project_id = create_project(db, "Les territoires de verre")
    image_id = db.run(
        """INSERT INTO image_library(project_id,title,category,image_data,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Carte du royaume", "Carte", b"map-image", NOW(), NOW()),
    ).lastrowid
    location_id = db.run(
        """INSERT INTO locations(project_id,position,name,category,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, 0, "Cité du verre", "Ville", NOW(), NOW()),
    ).lastrowid
    map_id = db.run(
        """INSERT INTO geography_maps(
        project_id,name,scale_label,background_image_id,width,height,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, "Royaume central", "1 case = 10 km", image_id, 1800, 1200, NOW(), NOW()),
    ).lastrowid
    db.run(
        """INSERT INTO geography_markers(
        map_id,project_id,location_id,marker_type,label,notes,color,x,y,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (
            map_id, project_id, location_id, "Lieu", "La capitale", "Pouvoir royal",
            "#D84A32", 420.5, 315.25, NOW(), NOW(),
        ),
    )
    db.run(
        """INSERT INTO geography_markers(
        map_id,project_id,marker_type,label,notes,color,x,y,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            map_id, project_id, "Frontière", "Mur de brume", "Passage interdit",
            "#667788", 980, 640, NOW(), NOW(),
        ),
    )

    export_path = tmp_path / "geography.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)

    imported_map = db.one("SELECT * FROM geography_maps WHERE project_id=?", (imported_id,))
    imported_image = db.one("SELECT id FROM image_library WHERE project_id=?", (imported_id,))
    imported_location = db.one("SELECT id FROM locations WHERE project_id=?", (imported_id,))
    assert imported_map["name"] == "Royaume central"
    assert imported_map["scale_label"] == "1 case = 10 km"
    assert imported_map["background_image_id"] == imported_image["id"]
    markers = db.q(
        "SELECT * FROM geography_markers WHERE map_id=? ORDER BY id", (imported_map["id"],)
    )
    assert len(markers) == 2
    assert markers[0]["location_id"] == imported_location["id"]
    assert markers[0]["x"] == 420.5
    assert markers[1]["location_id"] is None
    assert markers[1]["marker_type"] == "Frontière"
    assert markers[1]["y"] == 640

    db.run("DELETE FROM geography_maps WHERE id=?", (imported_map["id"],))
    assert db.one("SELECT COUNT(*) FROM geography_markers WHERE project_id=?", (imported_id,))[0] == 0
    assert db.one("SELECT COUNT(*) FROM locations WHERE project_id=?", (imported_id,))[0] == 1
    assert db.one("SELECT COUNT(*) FROM image_library WHERE project_id=?", (imported_id,))[0] == 1
    db.conn.close()


def test_v018_theme_positions_and_motifs_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "theme.db")
    project_id = create_project(db, "La fenêtre fermée")
    character_id = db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    track_id = int(db.ensure_timeline_track(project_id, "Intrigue principale")["id"])
    event_id = db.run(
        """INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, track_id, "Mina ferme la fenêtre", NOW(), NOW()),
    ).lastrowid
    image_id = db.run(
        """INSERT INTO image_library(project_id,title,category,image_data,created_at,updated_at)
        VALUES(?,?,?,?,?,?)""",
        (project_id, "Fenêtre", "Objet", b"theme-image", NOW(), NOW()),
    ).lastrowid
    location_id = db.run(
        """INSERT INTO locations(project_id,position,name,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, 0, "Chambre de Mina", NOW(), NOW()),
    ).lastrowid
    db.run(
        """INSERT INTO theme_profiles(
        project_id,theme_word,central_question,personal_interest,avoid_message,opening_view,
        decisions_note,consequences_note,conflicts_note,ending_response,notes,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, "Confiance", "Peut-on protéger sans contrôler ?", "La frontière m'intéresse.",
            "La confiance résout tout.", "Mina pense devoir tout vérifier.", "Elle refuse de déléguer.",
            "Elle isole son alliée.", "Protection contre liberté.", "Elle accepte l'incertitude.",
            "Garder une fin ambiguë.", NOW(), NOW(),
        ),
    )
    position_id = db.run(
        """INSERT INTO theme_positions(
        project_id,position,position_type,label,stance,nuance,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, 0, "main", "Contrôler protège", "Mina le croit.", "Cela l'isole.", NOW(), NOW()),
    ).lastrowid
    db.run(
        "INSERT INTO theme_position_characters(position_id,character_id) VALUES(?,?)",
        (position_id, character_id),
    )
    motif_id = db.run(
        """INSERT INTO theme_motifs(
        project_id,position,name,motif_type,meaning,appearances,evolution,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?)""",
        (project_id, 0, "La fenêtre", "Objet", "La confiance", "Trois retours", "Elle s'ouvre", NOW(), NOW()),
    ).lastrowid
    for table, column, target_id in (
        ("theme_motif_locations", "location_id", location_id),
        ("theme_motif_events", "event_id", event_id),
        ("theme_motif_images", "image_id", image_id),
    ):
        db.run(f"INSERT INTO {table}(motif_id,{column}) VALUES(?,?)", (motif_id, target_id))

    export_path = tmp_path / "theme.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    assert db.one("SELECT central_question FROM theme_profiles WHERE project_id=?", (imported_id,))[0] == "Peut-on protéger sans contrôler ?"
    imported_position_id = int(db.one(
        "SELECT id FROM theme_positions WHERE project_id=?", (imported_id,)
    )[0])
    imported_motif_id = int(db.one(
        "SELECT id FROM theme_motifs WHERE project_id=?", (imported_id,)
    )[0])
    assert db.one(
        "SELECT COUNT(*) FROM theme_position_characters WHERE position_id=?", (imported_position_id,)
    )[0] == 1
    for table in ("theme_motif_locations", "theme_motif_events", "theme_motif_images"):
        assert db.one(f"SELECT COUNT(*) FROM {table} WHERE motif_id=?", (imported_motif_id,))[0] == 1
    db.conn.close()


def test_v019_conflicts_and_connections_survive_export_import(tmp_path: Path) -> None:
    db = Database(tmp_path / "conflicts.db")
    project_id = create_project(db, "La ville fermée")
    character_id = db.run(
        "INSERT INTO characters(project_id,name,role,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    group_id = db.run(
        "INSERT INTO character_groups(project_id,name,group_type,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, "Conseil", "Faction", NOW(), NOW()),
    ).lastrowid
    scene_id = db.run(
        "INSERT INTO scene_rows(project_id,position,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, 0, "La porte refuse de s’ouvrir", NOW(), NOW()),
    ).lastrowid
    node_id = db.create_story_map_node(
        project_id, "Premier refus", "Le Conseil bloque Mina.", "obstacle", 100, 100
    )
    track_id = int(db.ensure_timeline_track(project_id, "Intrigue principale")["id"])
    event_id = db.run(
        "INSERT INTO timeline_events(project_id,track_id,title,created_at,updated_at) VALUES(?,?,?,?,?)",
        (project_id, track_id, "Fermeture des portes", NOW(), NOW()),
    ).lastrowid
    theme_position_id = db.run(
        """INSERT INTO theme_positions(
        project_id,position,position_type,label,stance,nuance,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?)""",
        (project_id, 0, "main", "Obéir protège", "Le Conseil le croit.", "L’ordre enferme.", NOW(), NOW()),
    ).lastrowid
    conflict_id = db.run(
        """INSERT INTO conflicts(
        project_id,position,title,importance,nature,side_a_label,side_a_goal,
        side_b_label,side_b_goal,incompatibility,stakes,trigger_note,escalation,
        difficult_choice,decisive_confrontation,outcome,cost,change_note,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            project_id, 0, "Mina contre le Conseil", "primary", "social",
            "Mina", "Livrer la lettre", "Le Conseil", "Maintenir les portes fermées",
            "La lettre révèle un crime du Conseil.", "La liberté du frère de Mina",
            "Les portes ferment", "Mina devient recherchée", "Sauver une alliée ou atteindre le juge",
            "Mina lit la lettre en public", "Une enquête commence", "Elle perd son anonymat",
            "Mina choisit d’agir", NOW(), NOW(),
        ),
    ).lastrowid
    db.run(
        "INSERT INTO conflict_characters(conflict_id,character_id,side) VALUES(?,?,?)",
        (conflict_id, character_id, "a"),
    )
    db.run(
        "INSERT INTO conflict_groups(conflict_id,group_id,side) VALUES(?,?,?)",
        (conflict_id, group_id, "b"),
    )
    for table, column, target_id in (
        ("conflict_scenes", "scene_id", scene_id),
        ("conflict_story_nodes", "node_id", node_id),
        ("conflict_events", "event_id", event_id),
        ("conflict_theme_positions", "position_id", theme_position_id),
    ):
        db.run(f"INSERT INTO {table}(conflict_id,{column}) VALUES(?,?)", (conflict_id, target_id))

    export_path = tmp_path / "conflicts.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    imported_conflict = db.one("SELECT * FROM conflicts WHERE project_id=?", (imported_id,))
    assert imported_conflict["title"] == "Mina contre le Conseil"
    assert imported_conflict["importance"] == "primary"
    assert imported_conflict["difficult_choice"].startswith("Sauver une alliée")
    for table in (
        "conflict_characters", "conflict_groups", "conflict_scenes",
        "conflict_story_nodes", "conflict_events", "conflict_theme_positions",
    ):
        assert db.one(
            f"SELECT COUNT(*) FROM {table} WHERE conflict_id=?", (int(imported_conflict["id"]),)
        )[0] == 1
    db.conn.close()


def test_v025_tags_are_shared_and_survive_project_export(tmp_path: Path) -> None:
    db = Database(tmp_path / "tags.db")
    project_id = create_project(db, "Projet étiqueté")
    character_id = db.run(
        """INSERT INTO characters(project_id,name,role,created_at,updated_at)
        VALUES(?,?,?,?,?)""",
        (project_id, "Mina", "Protagoniste", NOW(), NOW()),
    ).lastrowid
    document = db.ensure_doc(project_id, "synopsis", "Synopsis")

    db.set_entity_tags(
        project_id, "character", character_id, ["Principal", "À revoir", "principal"]
    )
    db.set_entity_tags(project_id, "document", int(document["id"]), ["À revoir"])
    assert set(db.entity_tag_names(project_id, "character", character_id)) == {
        "À revoir",
        "Principal",
    }
    assert db.one(
        "SELECT COUNT(*) FROM tags WHERE project_id=?", (project_id,)
    )[0] == 2

    export_path = tmp_path / "tags.storyforge.json"
    db.export_project(project_id, export_path)
    imported_id = db.import_project(export_path)
    imported_character = db.one(
        "SELECT id FROM characters WHERE project_id=? AND name='Mina'", (imported_id,)
    )
    imported_document = db.one(
        "SELECT id FROM project_docs WHERE project_id=? AND doc_type='synopsis'",
        (imported_id,),
    )
    assert set(db.entity_tag_names(
        imported_id, "character", int(imported_character["id"])
    )) == {"À revoir", "Principal"}
    assert db.entity_tag_names(
        imported_id, "document", int(imported_document["id"])
    ) == ["À revoir"]
    db.conn.close()
