"""pdf — PDF inspection (read-only).

4 subcommands
-------------
pages          page_count, per-page width/height + orientation (landscape/portrait).
text-dump      extract text from all (or a page-range) pages.
cjk-check      whether the PDF embeds CJK-capable fonts; useful for "中文乱码" rubric.
count-images   count embedded image XObjects across the document (or per page).
"""
from __future__ import annotations

import argparse
import re
from typing import Any

from . import _common as C

_PDF_EXTS = (".pdf",)


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("pages", help="page count + per-page dimensions + orientation.")
    p.add_argument("file")
    p.add_argument("--expect-orientation", choices=("portrait", "landscape"), default=None,
                   help="if set, ALL pages must match this orientation to pass")
    p.add_argument("--min-pages", type=int, default=None)
    p.add_argument("--max-pages", type=int, default=None)

    p = sub.add_parser("text-dump", help="extract text from a page range.")
    p.add_argument("file")
    p.add_argument("--start", type=int, default=1, help="1-based, inclusive")
    p.add_argument("--end", type=int, default=None, help="1-based, inclusive (default: last page)")
    p.add_argument("--max-chars", type=int, default=20000)

    p = sub.add_parser("cjk-check",
                       help="check whether PDF embeds CJK-capable fonts (proxy for correct Chinese rendering).")
    p.add_argument("file")
    p.add_argument("--sample-pages", type=int, default=3,
                   help="how many pages to sample for actual text inspection")

    p = sub.add_parser("count-images",
                       help="count embedded image XObjects across the document (or per page).")
    p.add_argument("file")
    p.add_argument("--per-page", action="store_true",
                   help="also emit a per-page count list (capped at 50 pages)")
    p.add_argument("--min", type=int, default=None,
                   help="optional lower bound to assert on")


# ---------------------------------------------------------------------------
# Helpers — try pdfplumber first (better text extraction), fall back to pypdf.
# ---------------------------------------------------------------------------

def _open_plumber(path: str):
    pdfplumber = C.lazy_import("pdfplumber", hint="pip install pdfplumber")
    abs_path = C.require_file(path, _PDF_EXTS)
    try:
        return pdfplumber.open(abs_path), abs_path
    except Exception as e:
        raise C.VerifierError(C.ErrCode.PARSE_ERROR,
                              f"pdfplumber.open({abs_path}) failed: {e}") from e


def _open_pypdf(path: str):
    pypdf = C.lazy_import("pypdf", hint="pip install pypdf")
    abs_path = C.require_file(path, _PDF_EXTS)
    try:
        return pypdf.PdfReader(abs_path), abs_path
    except Exception as e:
        raise C.VerifierError(C.ErrCode.PARSE_ERROR,
                              f"pypdf.PdfReader({abs_path}) failed: {e}") from e


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------

def _orientation(width: float, height: float) -> str:
    return "landscape" if width > height else "portrait"


def cmd_pages(args: argparse.Namespace) -> dict:
    pdf, abs_path = _open_plumber(args.file)
    try:
        n = len(pdf.pages)
        pages_info = []
        for i, page in enumerate(pdf.pages[:50]):  # cap dump for safety
            w = float(page.width)
            h = float(page.height)
            pages_info.append({
                "page": i + 1,
                "width": w,
                "height": h,
                "orientation": _orientation(w, h),
            })
    finally:
        pdf.close()

    checks: list[dict] = []
    if args.min_pages is not None:
        checks.append({"check": "min_pages", "expected": args.min_pages,
                       "actual": n, "passed": n >= args.min_pages})
    if args.max_pages is not None:
        checks.append({"check": "max_pages", "expected": args.max_pages,
                       "actual": n, "passed": n <= args.max_pages})
    if args.expect_orientation is not None:
        # Need orientation for ALL pages, not just the sample. If n>50 we re-open
        # to scan tail pages (fast, only metadata accessed).
        all_orient: list[str] = [p["orientation"] for p in pages_info]
        if n > len(pages_info):
            pdf2, _ = _open_plumber(args.file)
            try:
                for page in pdf2.pages[len(pages_info):]:
                    all_orient.append(_orientation(float(page.width), float(page.height)))
            finally:
                pdf2.close()
        mismatched = [i + 1 for i, o in enumerate(all_orient) if o != args.expect_orientation]
        checks.append({
            "check": "orientation",
            "expected": args.expect_orientation,
            "actual_unique": sorted(set(all_orient)),
            "mismatched_pages": mismatched[:10],
            "passed": not mismatched,
        })
    overall: bool | None = all(c["passed"] for c in checks) if checks else None

    return {
        "file": abs_path, "page_count": n,
        "pages_sample": pages_info,
        "checks": checks, "passed": overall,
        "_evidence": C.evidence(
            file=abs_path,
            quote=f"page_count={n}"
            + (f"; first: {pages_info[0]['width']:.0f}×{pages_info[0]['height']:.0f} "
               f"({pages_info[0]['orientation']})" if pages_info else "")
            + ("; checks: " + ", ".join(f"{c['check']}={c['passed']}" for c in checks)
               if checks else ""),
        ),
    }


# ---------------------------------------------------------------------------
# text-dump
# ---------------------------------------------------------------------------

def cmd_text_dump(args: argparse.Namespace) -> dict:
    pdf, abs_path = _open_plumber(args.file)
    try:
        n = len(pdf.pages)
        start = max(1, args.start)
        end = n if args.end is None else min(n, args.end)
        if start > end:
            raise C.VerifierError(C.ErrCode.BAD_ARGS,
                                  f"invalid range: start={start} > end={end} (pages={n})")
        parts: list[str] = []
        for i in range(start - 1, end):
            parts.append(f"# page {i + 1}")
            parts.append(pdf.pages[i].extract_text() or "")
            if sum(len(p) for p in parts) > args.max_chars:
                break
    finally:
        pdf.close()
    text = "\n".join(parts)
    truncated = len(text) > args.max_chars
    if truncated:
        text = text[: args.max_chars]
    return {
        "file": abs_path, "page_count": n,
        "start": start, "end": end,
        "char_count": len(text), "truncated": truncated, "text": text,
        "_evidence": C.evidence(file=abs_path,
                                locator={"pages": f"{start}-{end}"},
                                quote=f"{end - start + 1} pages, {len(text)} chars"
                                + (" (truncated)" if truncated else "")),
    }


# ---------------------------------------------------------------------------
# cjk-check
# ---------------------------------------------------------------------------

def _is_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in s)


def cmd_cjk_check(args: argparse.Namespace) -> dict:
    """Two heuristics:
    1. Embedded fonts: look for any /BaseFont with CJK indicators in pypdf.
    2. Sample text: extract first N pages with pdfplumber; count CJK glyphs.
    A PDF that "should be Chinese" but extracts almost no CJK chars indicates
    the underlying file likely shipped raster text or missing font subsets.
    """
    reader, abs_path = _open_pypdf(args.file)
    cjk_font_names: list[str] = []
    try:
        for page in reader.pages:
            try:
                resources = page.get("/Resources")
                if resources is None:
                    continue
                fonts = resources.get("/Font") if hasattr(resources, "get") else None
                if not fonts:
                    continue
                for k in fonts.keys():
                    fobj = fonts[k]
                    base = fobj.get("/BaseFont") if hasattr(fobj, "get") else None
                    if base and any(t in str(base) for t in
                                    ("SimSun", "STSong", "PingFang", "MS-", "MingLiU",
                                     "FangSong", "YaHei", "Hei", "Kai", "GBK", "GB2312",
                                     "Adobe-GB1", "Adobe-CNS1", "CJK")):
                        cjk_font_names.append(str(base))
            except Exception:
                continue
    except Exception:
        pass

    # Sample text
    pdf, _ = _open_plumber(args.file)
    cjk_chars = 0
    sampled_chars = 0
    try:
        for i, page in enumerate(pdf.pages):
            if i >= args.sample_pages:
                break
            txt = page.extract_text() or ""
            sampled_chars += len(txt)
            cjk_chars += sum(1 for c in txt if "\u4e00" <= c <= "\u9fff")
    finally:
        pdf.close()

    has_cjk_text = cjk_chars > 0
    has_cjk_font = bool(cjk_font_names)
    return {
        "file": abs_path,
        "has_cjk_font": has_cjk_font,
        "cjk_font_names": list(set(cjk_font_names))[:10],
        "sampled_pages": min(args.sample_pages, len(reader.pages)),
        "sampled_total_chars": sampled_chars,
        "cjk_chars_in_sample": cjk_chars,
        "has_cjk_text": has_cjk_text,
        "_evidence": C.evidence(file=abs_path,
                                quote=f"cjk_font={has_cjk_font} ({len(set(cjk_font_names))} fonts), "
                                f"cjk_text={has_cjk_text} ({cjk_chars}/{sampled_chars} in {args.sample_pages} pages)"),
    }


# ---------------------------------------------------------------------------
# count-images — count Image XObjects across the document.
#
# Strategy: walk page resources via pypdf (more robust than pdfplumber's
# page.images for non-raster image variants).  We follow the standard PDF
# pattern: /Resources/XObject/<key> with /Subtype = /Image.
# ---------------------------------------------------------------------------

def _count_page_images_pypdf(page) -> int:
    try:
        resources = page.get("/Resources")
    except Exception:
        return 0
    if resources is None:
        return 0
    try:
        xobjects = resources.get("/XObject")
    except Exception:
        xobjects = None
    if not xobjects:
        return 0
    n = 0
    try:
        for key in xobjects.keys():
            obj = xobjects[key]
            try:
                subtype = obj.get("/Subtype")
            except Exception:
                subtype = None
            if subtype is not None and str(subtype) == "/Image":
                n += 1
    except Exception:
        return n
    return n


def cmd_count_images(args: argparse.Namespace) -> dict:
    reader, abs_path = _open_pypdf(args.file)
    total = 0
    per_page: list[dict] = []
    for i, page in enumerate(reader.pages):
        n = _count_page_images_pypdf(page)
        total += n
        if args.per_page and i < 50:
            per_page.append({"page": i + 1, "n_images": n})

    passed: bool | None = None
    if args.min is not None:
        passed = total >= args.min

    out = {
        "file": abs_path,
        "page_count": len(reader.pages),
        "n_images": total,
        "passed": passed,
        "_evidence": C.evidence(
            file=abs_path,
            quote=f"images={total} across {len(reader.pages)} pages"
            + (f"; min={args.min}: {'OK' if passed else 'FAIL'}"
               if args.min is not None else ""),
        ),
    }
    if args.per_page:
        out["per_page"] = per_page
    return out
