import json
import os
from pathlib import Path
import subprocess
import pytest
from storyforge_context.index import RepositoryIndex, MAX_RESPONSE, allowed


def git(root, *args):
    return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args], check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, 'init')
    git(tmp_path, 'config', 'user.name', 'Context test')
    git(tmp_path, 'config', 'user.email', 'test@example.invalid')
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'app.py').write_text('class Window:\n    def show_scene(self):\n        return "scénario"\n', encoding='utf8')
    (tmp_path / 'docs/FEATURES.md').write_text('| screenplay.editor | Éditeur | `app.py:show_scene` | `tests/test_scene.py` |\n', encoding='utf8')
    (tmp_path / 'docs/PRODUCT.md').write_text('# Produit\nApprendre avant de construire.\n', encoding='utf8')
    (tmp_path / 'tests/test_scene.py').write_text('def test_scene():\n    assert True\n')
    git(tmp_path, 'add', '.')
    git(tmp_path, 'commit', '-m', 'fixture')
    return tmp_path


def test_provenance_feature_mapping_incremental_and_delete(repository):
    index = RepositoryIndex(repository)
    result = index.feature('screenplay.editor')
    assert {r['path'] for r in result['results']} == {'docs/FEATURES.md', 'app.py', 'tests/test_scene.py'}
    assert result['revision'] == git(repository, 'rev-parse', 'HEAD').strip()
    assert all(len(r['sha256']) == 64 for r in result['results'])
    assert any(r['symbol'] == 'Window.show_scene' for r in result['results'])
    count = index.parsed_count
    index.search('scénario')
    assert index.parsed_count == count
    source = repository / 'app.py'
    source.write_text('def changed_scene():\n    return "Autre"\n')
    result = index.search('changed_scene')
    assert index.parsed_count == count + 1
    assert result['results'][0]['worktree_modified']
    assert not result['results'][0]['staged_modified']
    git(repository, 'add', 'app.py')
    result = index.search('changed_scene')
    assert result['results'][0]['staged_modified']
    source.unlink()
    assert not any(r['path'] == 'app.py' for r in index.search('scene')['results'])
    assert 'app.py' in index.errors


@pytest.mark.parametrize('path', ['storyforge.db', '.env', 'secrets.py', 'output/test.py', 'docs/archive/a.md', '../app.py', '/etc/passwd', 'tests/private.json', 'docs/STORY.md', 'content/sessions/private.json', 'content/sessions/../../storyforge.db'])
def test_allowlist_rejects_private_paths(path):
    assert not allowed(path)


@pytest.mark.parametrize('path', ['geography.py', 'content/sessions/session_01.json', 'content/sessions/guide_build_universe.json', 'content/sessions/guide_rewrite.json'])
def test_allowlist_accepts_static_geography_and_guide_sources(path):
    assert allowed(path)


def test_static_guide_and_geography_sources_are_searchable(repository):
    (repository / 'content/sessions').mkdir(parents=True)
    (repository / 'geography.py').write_text(
        'def render_geography_map():\n    return "REPERE_CARTOGRAPHIQUE"\n', encoding='utf8',
    )
    (repository / 'content/sessions/guide_build_universe.json').write_text(
        '{"question": "QUESTION_UNIVERS_STATIQUE"}', encoding='utf8',
    )
    git(repository, 'add', 'geography.py', 'content/sessions/guide_build_universe.json')
    git(repository, 'commit', '-m', 'static sources')
    index = RepositoryIndex(repository)
    assert index.search('REPERE_CARTOGRAPHIQUE')['results'][0]['path'] == 'geography.py'
    assert index.search('QUESTION_UNIVERS_STATIQUE')['results'][0]['path'] == 'content/sessions/guide_build_universe.json'


def test_excludes_tracked_private_untracked_and_symlink(repository, tmp_path_factory):
    for path in ('storyforge.db', '.env', 'secrets.py'):
        (repository / path).write_text('PRIVATE_SENTINEL')
    git(repository, 'add', '.')
    (repository / 'db.py').write_text('UNTRACKED_SENTINEL = 1')
    outside = tmp_path_factory.mktemp('outside') / 'private.py'
    outside.write_text('PRIVATE_SENTINEL = 1')
    (repository / 'app.py').unlink()
    (repository / 'app.py').symlink_to(outside)
    index = RepositoryIndex(repository)
    assert index.search('PRIVATE_SENTINEL')['results'] == []
    assert index.search('UNTRACKED_SENTINEL')['results'] == []
    assert 'app.py' in index.errors


def test_invalid_python_evicted_not_served_stale(repository):
    index = RepositoryIndex(repository)
    assert index.search('scénario')['results']
    (repository / 'app.py').write_text('class broken syntax')
    assert not any(r['path'] == 'app.py' for r in index.search('scénario')['results'])
    assert 'app.py' in index.errors


def test_context_limits_and_parameter_rejection(repository):
    (repository / 'app.py').write_text('\n'.join(f'def scene_{i}():\n    return "' + 'x' * 3000 + '"' for i in range(30)))
    index = RepositoryIndex(repository)
    assert len(json.dumps(index.search('scene', 8), ensure_ascii=False)) <= MAX_RESPONSE
    for query in ('', 'x' * 257):
        with pytest.raises(ValueError): index.search(query)
    for count in (0, 9, True, '3'):
        with pytest.raises(ValueError): index.search('scene', count)
    with pytest.raises(ValueError): index.document('../storyforge.db')
    with pytest.raises(ValueError): index.feature('../app.py')


def test_secret_material_and_hardlinks_rejected(repository, tmp_path_factory):
    index = RepositoryIndex(repository)
    (repository / 'app.py').write_text('token = "' + 'ghp_' + 'A' * 35 + '"')
    assert index.search('token')['results'] == []
    assert 'app.py' in index.errors
    outside = tmp_path_factory.mktemp('private-hardlink') / 'source'
    outside.write_text('PRIVATE_SENTINEL = 1')
    (repository / 'app.py').unlink()
    os.link(outside, repository / 'app.py')
    assert index.search('PRIVATE_SENTINEL')['results'] == []


def test_same_size_same_mtime_change_and_sources_never_executed(repository):
    source = repository / 'app.py'
    source.write_text('raise RuntimeError("DO_NOT_EXECUTE_A")\n')
    index = RepositoryIndex(repository)
    first = index.search('DO_NOT_EXECUTE_A')['results'][0]['sha256']
    original = source.stat()
    source.write_text('raise RuntimeError("DO_NOT_EXECUTE_B")\n')
    os.utime(source, ns=(original.st_atime_ns, original.st_mtime_ns))
    second = index.search('DO_NOT_EXECUTE_B')['results'][0]['sha256']
    assert first != second
