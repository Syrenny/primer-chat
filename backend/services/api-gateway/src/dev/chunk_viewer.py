# src/dev/chunk_viewer.py
import contextlib
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import gradio as gr
import httpx


# -----------------------------
# Конфиг клиента API
# -----------------------------
class ApiClient:
    def __init__(self, timeout: float = 15.0):
        self.base_url = "http://localhost:8000".rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        # Кука вида JSON: {"cookie_id": "<uuid>"}
        cookies = {
            "primer-chat-cookie": json.dumps(
                {"cookie_id": "b27f6f27-9374-448d-83b9-bac0691823d0"},
                separators=(",", ":"),
            )
        }
        self._client = httpx.AsyncClient(
            base_url=self.base_url, cookies=cookies, timeout=self.timeout
        )
        return self

    async def __aexit__(self, *exc):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        assert self._client is not None, "ApiClient must be used inside 'async with'"
        return self._client

    # ---------- Files ----------
    async def list_files(self) -> List[Dict[str, Any]]:
        r = await self.client.get("/api/files")
        r.raise_for_status()
        return r.json()

    async def file_status(self, file_id: UUID) -> Dict[str, Any]:
        r = await self.client.get(f"/api/files/{file_id}/status")
        r.raise_for_status()
        return r.json()

    async def signed_url(self, file_id: UUID) -> str:
        r = await self.client.get(f"/api/files/{file_id}/signed_url")
        r.raise_for_status()
        return r.json()["url"]

    async def list_file_chunks(self, file_id: UUID) -> List[Dict[str, Any]]:
        r = await self.client.get(f"/api/chunks/{file_id}")
        r.raise_for_status()
        return r.json()

    # ---------- History Meta ----------
    async def list_history_meta(self) -> List[Dict[str, Any]]:
        r = await self.client.get("/api/history_meta")
        r.raise_for_status()
        return r.json()

    async def get_history_meta(self, history_id: UUID) -> Dict[str, Any]:
        r = await self.client.get(f"/api/history_meta/{history_id}")
        r.raise_for_status()
        return r.json()

    # ---------- Retriever ----------
    async def retrieve(self, history_id: UUID, query: str) -> List[Dict[str, Any]]:
        payload = {"history_id": str(history_id), "query": query}
        r = await self.client.post("/api/chunks", json=payload)
        r.raise_for_status()
        return r.json()["chunks"]


# -----------------------------
# Вспомогательные форматтеры
# -----------------------------
def _positions_preview(positions: List[Dict[str, Any]]) -> str:
    if not positions:
        return ""
    first = positions[0]
    page = first.get("page", "?")
    return f"p.{page} (+{max(0, len(positions) - 1)})"


def _short(s: str, n: int = 220) -> str:
    s = s.replace("\n", " ").strip()
    return (s[:n] + "…") if len(s) > n else s


def chunks_to_table(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for ch in chunks:
        rows.append(
            {
                "file_id": ch.get("file_id"),
                "filename": ch.get("filename"),
                "html_tag": ch.get("html_tag"),
                "positions": _positions_preview(ch.get("positions", [])),
                "content": _short(ch.get("content", "")),
            }
        )
    return rows


def group_by_file(chunks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for ch in chunks:
        name = ch.get("filename") or ch.get("file_id") or "unknown"
        out.setdefault(name, []).append(ch)
    return out


def _normalize_choice(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, list):
        return value[0] if value else None
    return str(value)


# -----------------------------
# Gradio logic (async handlers)
# -----------------------------
async def refresh_files():
    async with ApiClient() as api:
        files = await api.list_files()
        choices = [
            (f"{f['filename']} ({f['file_id'][:8]})", f["file_id"]) for f in files
        ]
        default_value = choices[0][1] if choices else None
        return gr.update(
            choices=choices, value=default_value
        ), f"Найдено файлов: {len(files)}"


async def load_file_chunks(file_id):
    fid = _normalize_choice(file_id)
    if not fid:
        return "_Файл не выбран_", ""
    async with ApiClient() as api:
        status = await api.file_status(UUID(fid))
        if not status.get("is_indexed"):
            return "_Файл ещё индексируется_", ""
        chunks = await api.list_file_chunks(UUID(fid))

        parts = []
        for i, ch in enumerate(chunks, 1):
            pos = _positions_preview(ch.get("positions", []))
            tag = ch.get("html_tag", "")
            content = ch.get("content", "")
            fname = ch.get("filename", "")
            parts.append(
                f"### {i}. {fname}\n**Tag:** `{tag}` | **Pos:** {pos}\n\n> {content}\n"
            )

        md = "\n\n".join(parts) if parts else "_Чанков нет._"

        url = ""
        with contextlib.suppress(Exception):
            url = await api.signed_url(UUID(fid))

        return md, url


# ---- History meta / search ----
def _history_label(meta: Dict[str, Any]) -> str:
    hid = str(meta["history_id"])
    files = meta.get("files") or []
    reqs = meta.get("requests") or []
    return f"{hid[:8]} • files:{len(files)} • reqs:{len(reqs)}"


async def refresh_histories():
    async with ApiClient() as api:
        items = await api.list_history_meta()
        choices = [(_history_label(m), m["history_id"]) for m in items]
        default_value = choices[0][1] if choices else None
        return gr.update(
            choices=choices, value=default_value
        ), f"Найдено историй: {len(items)}"


async def show_history_details(history_choice):
    hid = _normalize_choice(history_choice)
    if not hid:
        return "_История не выбрана_"
    async with ApiClient() as api:
        meta = await api.get_history_meta(UUID(hid))
    files = meta.get("files", [])
    parts = [f"### История {hid}\n", f"**Файлы ({len(files)}):**"]
    if files:
        for f in files:
            parts.append(f"- {f['filename']} (`{f['file_id']}`)")
    else:
        parts.append("- _нет файлов_")
    return "\n".join(parts)


async def do_search(history_choice, query: str):
    hid = _normalize_choice(history_choice)
    if not (hid and query.strip()):
        return "_Укажи историю и запрос_", None, ""

    async with ApiClient() as api:
        chunks = await api.retrieve(UUID(hid), query.strip())

        # Рисуем так же, как в первой вкладке (последовательно)
        parts = []
        for i, ch in enumerate(chunks, 1):
            pos = _positions_preview(ch.get("positions", []))
            tag = ch.get("html_tag", "")
            content = ch.get("content", "")
            fname = ch.get("filename", "")
            parts.append(
                f"### {i}. {fname}\n**Tag:** `{tag}` | **Pos:** {pos}\n\n> {content}\n"
            )

        md = "\n\n".join(parts) if parts else "_Ничего не найдено._"
        return md, f"Найдено чанков: {len(chunks)}"


# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks(title="Primer-Chat: Chunk Viewer", theme=gr.themes.Soft()) as demo:
    # --- Вкладка «Файлы и чанки» ---
    with gr.Tab("📁 Файлы и чанки"):
        with gr.Row():
            btn_refresh_files = gr.Button("🔄 Обновить список файлов")
            files_info = gr.Markdown()
        files_dd = gr.Dropdown(
            choices=[],
            label="Выбери файл",
            allow_custom_value=False,
            multiselect=False,
        )

        chunks_md = gr.Markdown(label="Чанки файла")
        pdf_url = gr.Textbox(label="Signed PDF URL (read-only)", interactive=False)

        btn_refresh_files.click(
            refresh_files,
            outputs=[files_dd, files_info],
        ).then(
            load_file_chunks,
            inputs=[files_dd],
            outputs=[chunks_md, pdf_url],
        )

        files_dd.change(
            load_file_chunks,
            inputs=[files_dd],
            outputs=[chunks_md, pdf_url],
        )

    # --- Вкладка «Поиск по истории» ---
    with gr.Tab("🔎 Поиск по истории"):
        with gr.Row():
            btn_refresh_hist = gr.Button("🔄 Обновить истории")
            hist_info = gr.Markdown()
        histories_dd = gr.Dropdown(
            choices=[],
            label="История (history_id)",
            allow_custom_value=False,
            multiselect=False,
        )
        history_meta_md = gr.Markdown(label="Файлы истории")

        # Обновление списка историй и автопоказ деталей первой
        btn_refresh_hist.click(
            refresh_histories,
            outputs=[histories_dd, hist_info],
        ).then(
            show_history_details,
            inputs=[histories_dd],
            outputs=[history_meta_md],
        )

        # При смене истории — показываем файлы
        histories_dd.change(
            show_history_details,
            inputs=[histories_dd],
            outputs=[history_meta_md],
        )

        with gr.Row():
            query = gr.Textbox(
                label="Запрос",
                placeholder="найти определения, формулы, ...",
                lines=2,
            )
            btn_search = gr.Button("🔍 Искать")
        search_info = gr.Markdown()
        search_md = gr.Markdown(label="Результаты (группировано по файлам)")

        btn_search.click(
            do_search,
            inputs=[histories_dd, query],
            outputs=[search_md, search_info],
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
