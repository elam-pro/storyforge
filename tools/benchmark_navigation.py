"""Measure reconstructed views with 200 synthetic records in a temporary DB."""
import sys
import tempfile
from pathlib import Path
from statistics import median
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from app import StoryForgeWindow


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
        window.active_project = pid
        for name in ('show_locations', 'show_characters', 'show_story_overview'):
            times = []
            for _ in range(8):
                start = perf_counter()
                getattr(window, name)()
                app.processEvents()
                times.append(1000 * (perf_counter() - start))
            print(f'{name}: median={median(times):.2f}ms max={max(times):.2f}ms')
        window.autosave_timer.stop()
        window.close()
        app.processEvents()


if __name__ == '__main__':
    main()
