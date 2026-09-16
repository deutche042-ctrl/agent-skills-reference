"""HTML → screenshot rendering via headless Chromium CLI (no Playwright dep).

Drop-in replacement for the legacy Playwright-based implementation.

Why no Playwright
-----------------
The rollout sandbox image (``flow_mcp/mcp_vm_server:1.1.9.ca56ab76e8``) cannot
run ``playwright install chromium`` (sandbox security profile blocks the post-
install step). It does ship a system ``chromium-browser`` (Chromium 135), so
we drive headless Chromium directly via its CLI ``--screenshot`` flag and
slice the resulting PNG into pages with Pillow (already a transitive dep).

Public API contract (must match the legacy version 1:1)
-------------------------------------------------------
* ``async def render_html_screenshots(*, html_text=None, file_url=None,
  viewport_width=..., viewport_height=..., max_pages=...)``
  → keyword-only arguments, exactly one of ``html_text`` / ``file_url``.
* Returns ``tuple[list[PageImage], str | None]``:
  - on success → ``(pages, None)``
  - on graceful degradation → ``([], "<reason>")`` (e.g. chromium missing,
    chromium hung, render produced 0-byte PNG). The skill's manifest layer
    appends ``reason`` to ``manifest.warnings`` and falls back to text-only
    output, exactly like the old ``"playwright not installed"`` branch.

Verified flag set on flow_mcp/mcp_vm_server (Chromium 135). Crucially does
NOT include ``--single-process`` (SIGTRAP) or ``--no-zygote`` (45 s hang
under this sandbox). ``--disable-dev-shm-usage`` is required because the
sandbox's ``/dev/shm`` is only 64 MB.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile

from .constants import (
    DEFAULT_HTML_VIEWPORT_HEIGHT,
    DEFAULT_HTML_VIEWPORT_WIDTH,
    DEFAULT_MAX_PAGES_RENDER,
)
from .types import PageImage

logger = logging.getLogger(__name__)

_NETWORKIDLE_TIMEOUT_MS = 8000
_AFTER_LOAD_WAIT_MS = 500
_LONG_PAGE_SEGMENT_HEIGHT = 1600
_RENDER_TIMEOUT_SEC = 90.0
_CHROMIUM_MAX_WINDOW_HEIGHT = 32000  # Chromium hard cap on window-size height


def _find_chromium_binary() -> str | None:
    """Locate a Chromium binary on PATH. Returns None when none found."""
    for name in ("chromium-browser", "chromium", "google-chrome", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _build_chromium_argv(
    *,
    binary: str,
    url: str,
    width: int,
    full_height: int,
    out_png: str,
    user_data_dir: str,
) -> list[str]:
    """Verified-to-work flag set on flow_mcp/mcp_vm_server (Chromium 135).

    See module docstring for what is intentionally NOT included and why.
    """
    return [
        binary,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--disable-setuid-sandbox",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-features=VizDisplayCompositor",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        f"--virtual-time-budget={_NETWORKIDLE_TIMEOUT_MS}",
        f"--window-size={width},{full_height}",
        f"--user-data-dir={user_data_dir}",
        f"--screenshot={out_png}",
        url,
    ]


async def _run_chromium(
    argv: list[str],
    *,
    timeout_sec: float,
) -> tuple[int, bytes]:
    """Run chromium as an async subprocess. Returns (rc, stderr).

    stdout is dropped (chromium does not write structured output to it; only
    glog / metric chatter that's not useful here).
    """
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        proc.kill()
        try:
            await proc.communicate()
        except Exception:  # noqa: BLE001
            pass
        raise RuntimeError(
            f"chromium render timed out after {timeout_sec:.0f}s"
        )
    return proc.returncode or 0, stderr or b""


def _last_content_row(img) -> int:
    """Return the y-index of the last row that contains *content*.

    "Content" means a row whose pixel variance exceeds a small threshold —
    i.e. it is not a single uniform color. This catches both white-background
    pages and cream / dark-themed pages where the body is filled with the
    document's background color but no glyphs / borders are drawn.

    Scanning samples every 8th pixel for speed (good enough for 1280-wide).
    """
    rgb = img.convert("RGB")
    w, h = rgb.size
    if w == 0 or h == 0:
        return -1
    px = rgb.load()
    for y in range(h - 1, -1, -1):
        rs: list[int] = []
        gs: list[int] = []
        bs: list[int] = []
        for x in range(0, w, 8):
            r, g, b = px[x, y]
            rs.append(r)
            gs.append(g)
            bs.append(b)
        spread = (
            (max(rs) - min(rs))
            + (max(gs) - min(gs))
            + (max(bs) - min(bs))
        )
        if spread > 24:
            return y
    return -1


def _slice_png_into_pages(
    png_bytes: bytes,
    *,
    segment_height: int,
    max_pages: int,
) -> list[PageImage]:
    """Slice one tall PNG into multiple PageImage segments (Pillow-based).

    Pillow is already a transitive dep of artifact-preview (used by collage /
    docx / xlsx). Available in the sandbox.
    """
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(png_bytes))
    w, h = img.size

    bbox_h = _last_content_row(img) + 1
    if bbox_h <= 0:
        bbox_h = h
    img = img.crop((0, 0, w, bbox_h))
    w, h = img.size

    pages: list[PageImage] = []
    if h <= int(segment_height * 1.5):
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        pages.append(PageImage(
            page=1,
            png_bytes=buf.getvalue(),
            width=w,
            height=h,
        ))
        return pages

    n = min(max_pages, max(1, (h + segment_height - 1) // segment_height))
    for i in range(n):
        top = i * segment_height
        bot = min(h, top + segment_height)
        if top >= h:
            break
        if bot - top <= 10:
            break
        seg = img.crop((0, top, w, bot))
        buf = BytesIO()
        seg.save(buf, format="PNG", optimize=True)
        pages.append(PageImage(
            page=i + 1,
            png_bytes=buf.getvalue(),
            width=seg.width,
            height=seg.height,
        ))
    return pages


async def render_html_screenshots(
    *,
    html_text: str | None = None,
    file_url: str | None = None,
    viewport_width: int = DEFAULT_HTML_VIEWPORT_WIDTH,
    viewport_height: int = DEFAULT_HTML_VIEWPORT_HEIGHT,
    max_pages: int = DEFAULT_MAX_PAGES_RENDER,
) -> tuple[list[PageImage], str | None]:
    """Render an HTML document via headless Chromium, returning PNG pages.

    Exactly one of ``html_text`` or ``file_url`` must be provided:

    * ``html_text`` → written to a tempfile and loaded via ``file://`` URL
      (chromium has no equivalent of Playwright's ``page.set_content``).
    * ``file_url`` → loaded directly (relative assets work as long as
      they're on disk next to the file).

    Returns
    -------
    (pages, error)
        Same convention as the legacy Playwright version: empty list +
        diagnostic on failure / missing chromium; non-empty list +
        ``None`` on success.
    """
    if (html_text is None) == (file_url is None):
        raise ValueError("exactly one of html_text / file_url must be set")

    binary = _find_chromium_binary()
    if binary is None:
        return [], (
            "chromium not installed (looked for chromium-browser, "
            "chromium, google-chrome, chrome on PATH)"
        )

    full_height = max(viewport_height, _LONG_PAGE_SEGMENT_HEIGHT) * max(
        1, max_pages,
    )
    full_height = min(full_height, _CHROMIUM_MAX_WINDOW_HEIGHT)

    workdir = tempfile.mkdtemp(prefix="artifact_preview_html_")
    try:
        if html_text is not None:
            html_path = os.path.join(workdir, "input.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_text)
            url = f"file://{html_path}"
        else:
            assert file_url is not None
            url = file_url

        out_png = os.path.join(workdir, "page.png")
        user_data = os.path.join(workdir, "profile")
        os.makedirs(user_data, exist_ok=True)
        argv = _build_chromium_argv(
            binary=binary,
            url=url,
            width=viewport_width,
            full_height=full_height,
            out_png=out_png,
            user_data_dir=user_data,
        )
        logger.debug("chromium render argv: %s", argv)

        try:
            rc, stderr = await _run_chromium(
                argv, timeout_sec=_RENDER_TIMEOUT_SEC,
            )
        except RuntimeError as exc:
            return [], str(exc)
        except Exception as exc:  # noqa: BLE001
            return [], f"chromium render failed: {exc}"

        if not os.path.isfile(out_png) or os.path.getsize(out_png) == 0:
            stderr_excerpt = stderr.decode("utf-8", "replace")[:500]
            return [], (
                f"chromium render produced no PNG (rc={rc}): "
                f"stderr={stderr_excerpt}"
            )

        with open(out_png, "rb") as f:
            png_bytes = f.read()

        try:
            pages = _slice_png_into_pages(
                png_bytes,
                segment_height=_LONG_PAGE_SEGMENT_HEIGHT,
                max_pages=max_pages,
            )
        except Exception as exc:  # noqa: BLE001
            return [], f"png slice failed: {exc}"

        if not pages:
            return [], "chromium render produced no pages after slicing"
        return pages, None
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
