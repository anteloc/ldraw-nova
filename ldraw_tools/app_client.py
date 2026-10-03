"""Bounded workflow client for the local ldraw-nova-docker web app."""
from __future__ import annotations

import asyncio
import base64
import ipaddress
import json
import re
from typing import Any
from urllib.parse import quote, urlencode, urlsplit

import httpx

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")


class AppError(ValueError):
    """An actionable error safe to show to an MCP client."""


def identifier(value: str) -> str:
    if not ID_RE.fullmatch(value):
        raise AppError("Invalid chat, model configuration, or approval ID.")
    return value


def model_name(value: str) -> str:
    if (not value or len(value.encode()) > 255 or value.startswith('.')
            or any(c in value for c in '/\\') or any(ord(c) < 32 for c in value)
            or value.lower().rsplit('.', 1)[-1] not in ('mpd', 'ldr', 'dat')):
        raise AppError("Use a model filename ending in .mpd, .ldr, or .dat, without folders.")
    return value


def prompt_text(value: str) -> str:
    if not value.strip() or len(value) > 200_000:
        raise AppError("Provide a nonempty prompt of at most 200,000 characters.")
    return value


class NovaApp:
    def __init__(self, base_url: str = 'http://127.0.0.1:8765', *,
                 transport: httpx.AsyncBaseTransport | None = None):
        url = urlsplit(base_url)
        try:
            local = url.hostname == 'localhost' or ipaddress.ip_address(url.hostname or '').is_loopback
        except ValueError:
            local = False
        if (not local or url.scheme not in ('http', 'https') or url.username or url.password
                or url.path not in ('', '/') or url.query or url.fragment):
            raise AppError("The app URL must be a loopback HTTP(S) origin, such as http://127.0.0.1:8765.")
        try:
            url.port
        except ValueError:
            raise AppError("Invalid app port.") from None
        self.base_url = base_url.rstrip('/')
        self.transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, transport=self.transport,
                                 timeout=15, follow_redirects=False, trust_env=False)

    @staticmethod
    def _check(response: httpx.Response) -> None:
        if response.is_success:
            return
        messages = {
            400: "The app rejected the request. Check the prompt and LLM provider in Settings.",
            404: "The requested chat or model was not found.",
            409: "The chat is already running, or this approval is no longer pending.",
            413: "The app rejected an oversized request.",
            422: "The app rejected invalid input.",
        }
        raise AppError(messages.get(response.status_code, "The app request failed. Check the app's logs and Settings."))

    async def _bytes(self, method: str, path: str, *, body: dict | None = None,
                     limit: int = MAX_JSON_BYTES) -> bytes:
        try:
            async with self._client() as client, client.stream(method, path, json=body) as response:
                self._check(response)
                data = bytearray()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if len(data) > limit:
                        raise AppError("The app response is too large; open the model in the web app instead.")
                return bytes(data)
        except httpx.HTTPError:
            raise AppError("Cannot reach LDraw Nova. Start its Docker app and check --app-url.") from None

    async def _json(self, method: str, path: str, body: dict | None = None) -> dict:
        try:
            value = json.loads(await self._bytes(method, path, body=body))
        except (ValueError, UnicodeError) as exc:
            if isinstance(exc, AppError):
                raise
            raise AppError("The app returned invalid JSON. Check that its version supports this API.") from None
        if not isinstance(value, dict):
            raise AppError("The app returned an unexpected response.")
        return value

    def _model_path(self, filename: str, collection: str) -> str:
        if collection not in ('generated', 'gallery'):
            raise AppError("Collection must be generated or gallery.")
        prefix = '/files/generated/' if collection == 'generated' else '/gallery-files/'
        return prefix + quote(model_name(filename), safe='')

    def _model(self, info: dict, collection: str) -> dict:
        path = self._model_path(info['file'], collection)
        result = {k: info.get(k) for k in ('file', 'name', 'description', 'parts', 'status',
                                         'bom_status', 'warnings', 'id') if k in info}
        result.update(collection=collection, model_url=self.base_url + path,
                      viewer_url=self.base_url + '/viewer/viewer.html?' + urlencode({'model': path}),
                      glb_url=self.base_url + '/api/glb?' + urlencode({'url': path}),
                      resource_uri=f"nova://models/{collection}/{quote(info['file'], safe='')}")
        stem = path.rsplit('.', 1)[0]
        for key, suffix in (('image_url', '.png'), ('bom_url', '.csv')):
            result[key] = self.base_url + stem + suffix if info.get(key) else None
        return result

    async def status(self) -> dict:
        data = await self._json('GET', '/api/llm-models')
        models = [{k: m.get(k) for k in ('id', 'model_name', 'auth_mode')} for m in data.get('models', [])]
        return {'app_url': self.base_url, 'settings_url': self.base_url + '/settings',
                'llm_models': models, 'default_id': data.get('default_id'),
                'ready': bool(models), 'permissions': 'ask',
                'note': 'Provider login/model access must also be valid. Generation uses the app provider and may incur its costs.'}

    async def list_models(self, collection: str = 'generated', limit: int = 20, offset: int = 0) -> dict:
        if collection not in ('generated', 'gallery') or not 1 <= limit <= 100 or offset < 0:
            raise AppError("Use generated or gallery, limit 1–100, and a nonnegative offset.")
        data = await self._json('GET', '/api/models' if collection == 'generated' else '/api/gallery')
        models = data.get('models', [])
        return {'models': [self._model(m, collection) for m in models[offset:offset + limit]],
                'total': len(models), 'offset': offset, 'pending': data.get('pending', 0)}

    async def read_model(self, filename: str, collection: str = 'generated') -> str:
        data = await self._bytes('GET', self._model_path(filename, collection), limit=MAX_FILE_BYTES)
        try:
            return data.decode('utf-8')
        except UnicodeError:
            raise AppError("The model is not UTF-8 LDraw text.") from None

    async def preview(self, filename: str, collection: str = 'generated') -> bytes:
        path = self._model_path(filename, collection).rsplit('.', 1)[0] + '.png'
        data = await self._bytes('GET', path, limit=MAX_FILE_BYTES)
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise AppError("The preview is not a PNG image.")
        return data

    async def generate(self, prompt: str, llm_model_id: str | None = None,
                       reference_model: str | None = None, collection: str = 'generated') -> dict:
        prompt_text(prompt)
        if llm_model_id:
            identifier(llm_model_id)
        documents = []
        if reference_model:
            source = await self.read_model(reference_model, collection)
            documents.append({'name': reference_model,
                              'data': 'data:text/plain;base64,' + base64.b64encode(source.encode()).decode()})
        configured = await self.status()
        if not configured['ready']:
            raise AppError("No LLM provider configured. Add or sign in to one in the app's Settings first.")
        if llm_model_id and llm_model_id not in {m['id'] for m in configured['llm_models']}:
            raise AppError("Unknown LLM configuration ID. Use get_app_status to list available IDs.")
        chat = await self._json('POST', '/api/chats', {'llm_model_id': llm_model_id})
        chat_id = identifier(chat['id'])
        try:
            await self._send(chat_id, prompt, llm_model_id, documents)
        except AppError:
            raise AppError(f"Generation could not start. Chat {chat_id} is preserved; check Settings and continue it with edit_model.") from None
        return {'chat_id': chat_id, 'status': 'started', 'chat_url': self.base_url + '/chat/' + chat_id,
                'next': 'Call get_generation. Ask the user before resolving any pending approvals.'}

    async def _send(self, chat_id: str, prompt: str, llm_model_id: str | None,
                    documents: list | None = None) -> dict:
        return await self._json('POST', f'/api/chats/{identifier(chat_id)}/messages',
                                {'text': prompt_text(prompt), 'llm_model_id': llm_model_id,
                                 'options': {'mode': 'agent', 'permissions': 'ask'},
                                 'documents': documents or []})

    async def edit(self, chat_id: str, prompt: str) -> dict:
        await self._send(chat_id, prompt, None)
        return {'chat_id': chat_id, 'status': 'started', 'chat_url': self.base_url + '/chat/' + chat_id,
                'next': 'Call get_generation to follow this revision. Previous models remain in the app.'}

    async def _snapshot(self, chat_id: str) -> dict:
        # Read only the initial SSE snapshot: do not hold an MCP call open for an entire build.
        try:
            async with self._client() as client, client.stream('GET', f'/api/chats/{chat_id}/stream') as response:
                self._check(response)
                lines, size = [], 0
                async for line in response.aiter_lines():
                    size += len(line)
                    if size > 256_000:
                        break
                    if line.startswith('data:'):
                        lines.append(line[5:].lstrip())
                    elif not line and lines:
                        value = json.loads('\n'.join(lines))
                        return value if isinstance(value, dict) else {}
        except (httpx.HTTPError, ValueError):
            pass
        return {}

    async def generation(self, chat_id: str, wait_seconds: int = 0) -> dict:
        identifier(chat_id)
        if not 0 <= wait_seconds <= 20:
            raise AppError("wait_seconds must be between 0 and 20.")
        deadline = asyncio.get_running_loop().time() + wait_seconds
        while True:
            data = await self._json('GET', f'/api/chats/{chat_id}')
            running = data['chat'].get('running', False)
            snapshot = await self._snapshot(chat_id) if running else {}
            approvals = snapshot.get('approvals', [])
            if not running or approvals or asyncio.get_running_loop().time() >= deadline:
                break
            await asyncio.sleep(min(2, max(0, deadline - asyncio.get_running_loop().time())))
        messages = data.get('messages', [])
        user = max((i for i, m in enumerate(messages) if m.get('role') == 'user' and not m.get('_hidden')), default=-1)
        turn = messages[user + 1:]
        last = next((m for m in reversed(turn) if m.get('role') == 'assistant'), {})
        text = last.get('content') if isinstance(last.get('content'), str) else ''
        if running:
            status = 'awaiting_approval' if approvals else 'running'
        elif last.get('_error'):
            status = 'failed'
        elif last.get('_notice'):
            status = 'cancelled' if text == 'Stopped.' else 'needs_continuation'
        elif last and not last.get('tool_calls'):
            status = 'completed'
        else:
            status = 'interrupted' if user >= 0 else 'idle'
        models = data.get('models', {})
        return {'chat_id': chat_id, 'status': status, 'running': running,
                'chat_url': self.base_url + '/chat/' + chat_id, 'message': text[-8000:],
                'approvals': approvals, 'activity': snapshot.get('activity'),
                'models': [self._model(m, 'generated') for m in models.values()],
                'note': 'Completed means the agent turn ended; review models and artifact statuses before claiming a successful build.'}

    async def cancel(self, chat_id: str) -> dict:
        return await self._json('POST', f'/api/chats/{identifier(chat_id)}/cancel')

    async def approve(self, chat_id: str, approval_id: str, approved: bool) -> dict:
        return await self._json('POST', f'/api/chats/{identifier(chat_id)}/approvals/{identifier(approval_id)}',
                                {'approved': approved})
