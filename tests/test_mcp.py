"""MCP workflow/protocol contracts without provider calls or Docker dependencies."""
import asyncio
import base64
import json
import sys

import pytest

pytest.importorskip('mcp')
httpx = pytest.importorskip('httpx')
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.memory import create_connected_server_and_client_session

from ldraw_tools.app_client import AppError, MAX_FILE_BYTES, NovaApp
from ldraw_tools.mcp_server import create_server


class AppFixture:
    def __init__(self):
        self.calls = []
        self.running = True
        self.configured = True
        self.approvals = []
        self.messages = [{'role': 'user', 'content': 'A castle'}]
        self.status_code = None
        self.model = {'file': 'castle.mpd', 'name': 'Castle', 'model_url': '/files/generated/castle.mpd',
                      'image_url': '/files/generated/castle.png', 'bom_url': '/files/generated/castle.csv',
                      'status': 'ready', 'bom_status': 'ready', 'parts': 42}
        self.source = b'0 A castle\n0 Name: castle.ldr\n'

    def handle(self, request):
        body = json.loads(request.content) if request.content else None
        self.calls.append((request.method, request.url.path, body))
        path = request.url.path
        if self.status_code:
            return httpx.Response(self.status_code, json={'detail': 'secret-provider-key'})
        if path == '/api/llm-models':
            models = [{'id': 'builder', 'model_name': 'Builder', 'auth_mode': 'api_key',
                       'litellm_params': {'api_key': 'secret-provider-key'}}] if self.configured else []
            return httpx.Response(200, json={'models': models, 'default_id': 'builder'})
        if path in ('/api/models', '/api/gallery'):
            return httpx.Response(200, json={'models': [self.model], 'pending': 0})
        if path.endswith('/stream'):
            data = {'running': self.running, 'approvals': self.approvals, 'activity': {'phase': 'Building'}}
            return httpx.Response(200, text='event: snapshot\ndata: ' + json.dumps(data) + '\n\n',
                                  headers={'content-type': 'text/event-stream'})
        if path.endswith('/messages'):
            return httpx.Response(202, json={'started': True})
        if path.endswith('/cancel'):
            self.running = False
            return httpx.Response(200, json={'cancelled': True})
        if '/approvals/' in path:
            self.approvals = []
            return httpx.Response(200, json={'accepted': True})
        if path == '/api/chats' and request.method == 'POST':
            return httpx.Response(200, json={'id': 'chat-1'})
        if path == '/api/chats/chat-1':
            return httpx.Response(200, json={'chat': {'id': 'chat-1', 'running': self.running},
                                           'messages': self.messages, 'models': {'model-1': self.model}})
        if path.endswith('.png'):
            return httpx.Response(200, content=b'\x89PNG\r\n\x1a\npreview')
        if path.endswith('.mpd'):
            return httpx.Response(200, content=self.source)
        return httpx.Response(404)

    def app(self):
        return NovaApp(transport=httpx.MockTransport(self.handle))


@pytest.mark.parametrize('url', [
    'http://example.com', 'http://127.0.0.1.evil.test', 'file:///tmp/model',
    'http://user:password@localhost:8765', 'http://localhost:8765/config',
    'http://localhost:8765?secret=1', 'http://localhost:bad',
])
def test_only_loopback_origins(url):
    with pytest.raises(AppError):
        NovaApp(url)


@pytest.mark.parametrize('url', ['http://127.0.0.1:8765', 'http://localhost:8765/', 'http://[::1]:8765'])
def test_supported_origins(url):
    assert NovaApp(url).base_url == url.rstrip('/')


@pytest.mark.parametrize('filename', ['../config.json', 'a/b.mpd', 'a\\b.mpd', '.secret.mpd', 'a\n.mpd', 'a.exe', ''])
def test_model_path_traversal_rejected_before_request(filename):
    fixture = AppFixture()
    with pytest.raises(AppError):
        asyncio.run(fixture.app().read_model(filename))
    assert fixture.calls == []


def test_generation_and_reference_attachment_keep_approval_boundary():
    fixture = AppFixture()
    result = asyncio.run(fixture.app().generate('Improve this castle', 'builder', 'castle.mpd', 'gallery'))
    assert result['chat_id'] == 'chat-1'
    post = next(body for method, path, body in fixture.calls if path.endswith('/messages'))
    assert post['options'] == {'mode': 'agent', 'permissions': 'ask'}
    assert post['documents'][0]['name'] == 'castle.mpd'
    assert base64.b64decode(post['documents'][0]['data'].split(',')[1]) == fixture.source
    assert not any('/approvals/' in path for _, path, _ in fixture.calls)


def test_provider_is_required_before_creating_chat():
    fixture = AppFixture()
    fixture.configured = False
    with pytest.raises(AppError, match='Settings'):
        asyncio.run(fixture.app().generate('Castle'))
    assert all(method == 'GET' for method, _, _ in fixture.calls)


def test_unknown_model_id_and_empty_prompts_do_not_create_chat():
    fixture = AppFixture()
    for prompt, model in [('Castle', 'unknown'), ('  ', None)]:
        with pytest.raises(AppError):
            asyncio.run(fixture.app().generate(prompt, model))
    assert all(method == 'GET' for method, _, _ in fixture.calls)


def test_provider_settings_never_expose_credentials():
    result = asyncio.run(AppFixture().app().status())
    assert result['ready']
    assert 'secret-provider-key' not in json.dumps(result)
    assert 'litellm_params' not in json.dumps(result)


@pytest.mark.parametrize('status', [400, 404, 409, 422, 500, 302])
def test_backend_errors_and_redirects_are_sanitized(status):
    fixture = AppFixture()
    fixture.status_code = status
    with pytest.raises(AppError) as error:
        asyncio.run(fixture.app().status())
    assert 'secret-provider-key' not in str(error.value)


def test_failed_start_preserves_chat_handle():
    fixture = AppFixture()
    def fail_start(request):
        if request.url.path.endswith('/messages'):
            return httpx.Response(400, json={'detail': 'secret-provider-key'})
        return fixture.handle(request)
    app = NovaApp(transport=httpx.MockTransport(fail_start))
    with pytest.raises(AppError, match='chat-1'):
        asyncio.run(app.generate('Castle'))
    assert not any(method == 'DELETE' for method, _, _ in fixture.calls)


@pytest.mark.parametrize('message, expected', [
    ({'role': 'assistant', 'content': 'Done'}, 'completed'),
    ({'role': 'assistant', '_error': True, 'content': 'Provider failed'}, 'failed'),
    ({'role': 'assistant', '_notice': True, 'content': 'Stopped.'}, 'cancelled'),
    ({'role': 'assistant', '_notice': True, 'content': 'Stopped after 80 steps.'}, 'needs_continuation'),
    ({'role': 'assistant', 'tool_calls': [{'id': 'call-1'}]}, 'interrupted'),
])
def test_terminal_status_does_not_treat_all_idle_turns_as_success(message, expected):
    fixture = AppFixture()
    fixture.running = False
    fixture.messages.append(message)
    assert asyncio.run(fixture.app().generation('chat-1'))['status'] == expected


def test_previous_turn_error_does_not_poison_revision():
    fixture = AppFixture()
    fixture.running = False
    fixture.messages = [{'role': 'assistant', '_error': True, 'content': 'Old error'},
                        {'role': 'user', 'content': 'Retry'}, {'role': 'assistant', 'content': 'Done'}]
    assert asyncio.run(fixture.app().generation('chat-1'))['status'] == 'completed'


def test_pending_approval_returns_early_and_requires_explicit_decision():
    fixture = AppFixture()
    fixture.approvals = [{'id': 'approval-1', 'name': 'run_shell', 'arguments': '{"command":"build"}'}]
    app = fixture.app()
    result = asyncio.run(app.generation('chat-1', 20))
    assert result['status'] == 'awaiting_approval'
    assert result['approvals'] == fixture.approvals
    assert not any('/approvals/' in path for _, path, _ in fixture.calls)
    assert asyncio.run(app.approve('chat-1', 'approval-1', False)) == {'accepted': True}
    assert fixture.calls[-1][2] == {'approved': False}


def test_revision_cancellation_and_links():
    fixture = AppFixture()
    app = fixture.app()
    assert asyncio.run(app.edit('chat-1', 'Make it taller'))['status'] == 'started'
    assert asyncio.run(app.cancel('chat-1')) == {'cancelled': True}
    model = asyncio.run(app.list_models('gallery'))['models'][0]
    assert model['model_url'] == 'http://127.0.0.1:8765/gallery-files/castle.mpd'
    assert model['resource_uri'] == 'nova://models/gallery/castle.mpd'
    assert '/api/glb?url=' in model['glb_url']


def test_large_model_is_bounded():
    fixture = AppFixture()
    fixture.source = b'a' * (MAX_FILE_BYTES + 1)
    with pytest.raises(AppError, match='too large'):
        asyncio.run(fixture.app().read_model('castle.mpd'))


@pytest.mark.parametrize('operation', [
    lambda app: app.generation('../config'), lambda app: app.generation('chat-1', 21),
    lambda app: app.list_models('config'), lambda app: app.list_models(limit=101),
    lambda app: app.list_models(offset=-1),
])
def test_invalid_inputs_fail_before_network(operation):
    fixture = AppFixture()
    with pytest.raises(AppError):
        asyncio.run(operation(fixture.app()))
    assert fixture.calls == []


def test_real_protocol_discovery_generate_poll_approve_edit_read_preview_and_cancel():
    async def scenario():
        fixture = AppFixture()
        async with create_connected_server_and_client_session(create_server(app=fixture.app())) as session:
            tools = (await session.list_tools()).tools
            assert {t.name for t in tools} == {
                'get_app_status', 'generate_model', 'edit_model', 'get_generation',
                'respond_to_approval', 'cancel_generation', 'list_models', 'read_model', 'preview_model'}
            assert next(t for t in tools if t.name == 'respond_to_approval').annotations.destructiveHint
            for tool, args in [
                ('get_app_status', {}), ('generate_model', {'prompt': 'Castle'}),
                ('get_generation', {'chat_id': 'chat-1'}),
                ('edit_model', {'chat_id': 'chat-1', 'prompt': 'Taller'}),
                ('list_models', {'collection': 'gallery'}),
                ('read_model', {'filename': 'castle.mpd'}),
            ]:
                assert not (await session.call_tool(tool, args)).isError
            preview = await session.call_tool('preview_model', {'filename': 'castle.mpd'})
            assert preview.content[0].type == 'image'
            fixture.approvals = [{'id': 'approval-1', 'name': 'run_shell', 'arguments': '{}'}]
            progress = await session.call_tool('get_generation', {'chat_id': 'chat-1'})
            assert progress.structuredContent['status'] == 'awaiting_approval'
            assert not (await session.call_tool('respond_to_approval', {
                'chat_id': 'chat-1', 'approval_id': 'approval-1', 'approved': False})).isError
            source = await session.read_resource('nova://models/gallery/castle.mpd')
            assert source.contents[0].text == fixture.source.decode()
            assert (await session.call_tool('read_model', {'filename': '../config.json'})).isError
            assert (await session.list_prompts()).prompts[0].name == 'design_lego_model'
            assert not (await session.call_tool('cancel_generation', {'chat_id': 'chat-1'})).isError
    asyncio.run(scenario())


def test_stdio_entry_point_initializes_without_a_running_app():
    async def scenario():
        params = StdioServerParameters(command=sys.executable, args=['-m', 'ldraw_tools.mcp_server'])
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            result = await session.initialize()
            assert result.serverInfo.name == 'LDraw Nova'
            assert len((await session.list_tools()).tools) == 9
    asyncio.run(scenario())
