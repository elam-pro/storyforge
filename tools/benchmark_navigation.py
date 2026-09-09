"""Measure heavy local views with synthetic records in a temporary DB."""
import sys
import tempfile
from pathlib import Path
from statistics import median
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from app import RelationshipMapDialog, StoryForgeWindow


def measure(label, repetitions, callback, app):
    times = []
    for _ in range(repetitions):
        start = perf_counter()
        callback()
        app.processEvents()
        times.append(1000 * (perf_counter() - start))
    print(f'{label}: median={median(times):.2f}ms max={max(times):.2f}ms')


def main():
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix='storyforge-benchmark-') as directory:
        window = StoryForgeWindow(Path(directory) / 'fixture.db')
        db = window.db
        pid = db.run("INSERT INTO projects(title,created_at,updated_at) VALUES('Synthetic','2026-09-08','2026-09-08')").lastrowid
        with db.transaction():
            for index in range(200):
                for table in ('characters', 'locations'):
                    db.run(f"INSERT INTO {table}(project_id,name,created_at,updated_at) VALUES(?,?,?,?)", (pid, f'Synthetic {index}', '2026-09-08', '2026-09-08'))
            tracks = [
                db.ensure_timeline_track(pid, name, color)
                for name, color in (
                    ('Intrigue', '#D84A32'), ('Backstory', '#376FC7'), ('Monde', '#37A56A')
                )
            ]
            for index in range(600):
                track = tracks[index % len(tracks)]
                db.run(
                    """INSERT INTO timeline_events(
                    project_id,track_id,time_hours,category,title,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?)""",
                    (pid, track['id'], index * 12 - 3600, 'Intrigue principale',
                     f'Événement {index}', '2026-09-08', '2026-09-08'),
                )
            relationship_map = db.ensure_relationship_map(pid)
            for index in range(199):
                db.run(
                    """INSERT INTO character_relationships(
                    project_id,map_id,character_a_id,character_b_id,relationship_type,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?)""",
                    (pid, relationship_map['id'], index + 1, index + 2, 'Lien',
                     '2026-09-08', '2026-09-08'),
                )
            geography_map_id = db.run(
                """INSERT INTO geography_maps(
                project_id,name,width,height,created_at,updated_at) VALUES(?,?,?,?,?,?)""",
                (pid, 'Monde synthétique', 3200, 2200, '2026-09-08', '2026-09-08'),
            ).lastrowid
            for index in range(600):
                db.run(
                    """INSERT INTO geography_markers(
                    project_id,map_id,label,marker_type,x,y,color,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (pid, geography_map_id, f'Repère {index}', 'Lieu',
                     40 + (index % 30) * 100, 40 + (index // 30) * 100,
                     '#D84A32', '2026-09-08', '2026-09-08'),
                )
        window.active_project = pid
        for name in ('show_locations', 'show_characters', 'show_story_overview'):
            measure(name, 8, getattr(window, name), app)
        measure('show_timeline (600 events)', 5, window.show_timeline, app)
        dialog = RelationshipMapDialog(window, db, pid, window.palette)
        measure('relationship map (200 nodes / 199 links)', 5, dialog._render_map, app)
        dialog.close()
        window.show_universe()
        app.processEvents()
        measure(
            'geography map (600 markers)', 5,
            lambda: window._load_geography_map(int(geography_map_id)), app,
        )
        window.autosave_timer.stop()
        window.close()
        app.processEvents()


if __name__ == '__main__':
    main()
