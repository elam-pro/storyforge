"""Real STDIO integration via the optional isolated SDK environment."""
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


def sdk_python():
    executable = ROOT / '.venv-mcp/bin/python'
    if executable.exists():
        return str(executable)
    try:
        import mcp
    except ImportError:
        pytest.skip('Optional MCP SDK missing; install requirements-mcp.txt in .venv-mcp')
    return sys.executable


CLIENT = r'''
import asyncio, json, sys
from mcp import Client
from mcp.client.stdio import StdioServerParameters

async def main():
    parameters = StdioServerParameters(command=sys.executable, args=['-B', '-m', 'storyforge_context.server', '--root', sys.argv[1]], cwd=sys.argv[2])
    async with Client(parameters, read_timeout_seconds=20, mode=sys.argv[3]) as client:
        tools = await client.list_tools()
        assert len(tools.tools) == 7
        names = {tool.name for tool in tools.tools}
        assert names == {'get_project_overview', 'get_architecture', 'get_decisions', 'search_project_docs', 'find_relevant_files', 'get_feature_context', 'get_project_context'}
        for tool in tools.tools:
            assert tool.annotations.read_only_hint and not tool.annotations.destructive_hint
            assert not tool.annotations.open_world_hint
        result = await client.call_tool('get_feature_context', {'feature_id': 'screenplay.editor'})
        assert not result.is_error
        data = result.structured_content
        assert data['results'] and data['revision']
        assert any(r['path'] == 'docs/FEATURES.md' for r in data['results'])
        for name, args in [('get_project_overview', {}), ('get_architecture', {}), ('get_decisions', {}), ('search_project_docs', {'query': 'scénario'}), ('find_relevant_files', {'query': 'script', 'limit': 8}), ('get_project_context', {'task': 'script'})]:
            response = await client.call_tool(name, args)
            assert not response.is_error, name
            assert len(json.dumps(response.structured_content, ensure_ascii=False)) <= 12000
        for args in ({'query': 'x' * 257}, {'query': 'script', 'limit': 9}, {'query': 'script', 'limit': True}):
            response = await client.call_tool('find_relevant_files', args)
            assert response.is_error
        response = await client.call_tool('get_feature_context', {'feature_id': '../storyforge.db'})
        assert response.is_error
        response = await client.call_tool('delete_project', {})
        assert response.is_error
        resources = await client.list_resources()
        assert len(resources.resources) == 5
        resource = await client.read_resource('storyforge://repository/product')
        assert json.loads(resource.contents[0].text)['scope']
        print('MCP STDIO integration OK')

asyncio.run(main())
'''


@pytest.mark.parametrize('mode', ['auto', 'legacy'])
def test_stdio_read_only_tools_resources_and_limits(tmp_path, mode):
    # Controlled repository containing sentinel private data, never personal files.
    def git(*args):
        subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(tmp_path), *args], check=True, capture_output=True)
    git('init')
    git('config', 'user.name', 'MCP test')
    git('config', 'user.email', 'mcp@example.invalid')
    (tmp_path / 'docs').mkdir()
    for name in ('PRODUCT', 'ARCHITECTURE', 'DECISIONS', 'ROADMAP'):
        (tmp_path / f'docs/{name}.md').write_text(f'# {name}\nScénario script.\n')
    (tmp_path / 'docs/FEATURES.md').write_text('| screenplay.editor | Script | `app.py:script` | |\n')
    (tmp_path / 'app.py').write_text('def script():\n    return "source"\n')
    (tmp_path / 'storyforge.db').write_bytes(b'PRIVATE_SENTINEL')
    git('add', '.')
    git('commit', '-m', 'fixture')
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    result = subprocess.run([sdk_python(), '-B', '-c', CLIENT, str(tmp_path), str(ROOT), mode], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'MCP STDIO integration OK' in result.stdout
    after = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert before == after
    assert 'PRIVATE_SENTINEL' not in result.stdout + result.stderr
