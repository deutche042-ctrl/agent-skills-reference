# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx", "lxml", "latex2mathml"]
# ///

"""
General-purpose .docx document generator: produces a standard-typography Word document directly from Markdown text.

Usage:
    uv run scripts/create_docx.py content.md output.docx
    uv run scripts/create_docx.py content.md output.docx --style patent
    uv run scripts/create_docx.py content.md output.docx --style official

The model outputs Markdown text directly, and the script parses the structure and generates a formatted .docx, with no intermediate JSON format needed.

Supported Markdown elements:
    # / ## / ### / ####   → headings (levels 1-4)
    plain text            → body paragraph (first-line indent)
    - / *                 → unordered list
    1. / 2.               → ordered list
    | col1 | col2 |       → table
    ```lang ... ```       → code block (gray background, Courier New monospace font)
    **text**              → bold
    $formula$             → inline OMML formula (LaTeX syntax, e.g. $\\frac{a}{b}$)
    $$formula$$           → standalone centered OMML formula (may include a number, e.g. $$formula$$ (4-3))
    ---                   → visual separator (a section break in patent mode)

Four typography styles (--style):
    general (default): general document (A4, 12pt body, bold headings, 2.5cm margins, 1.5 line spacing;
             Latin text in Times New Roman (body) / Arial (headings), with CJK falling back to 宋体/黑体)
    resume : resume (compact layout, 10pt body, 12/11/10.5pt headings, 1.15 line spacing,
             1.8cm margins, no first-line indent, no header/footer, targeting 1-2 pages)
    patent : patent document—automatically detects the H1 headings "Claims/Specification/Abstract"
             (or their Chinese equivalents 权利要求书/说明书/摘要) and splits into sections, each with its
             own header and page numbers; ordered lists are rendered as claim entries
    official: official document (GB/T 9704: 仿宋 (FangSong) size-three body text, 黑体 (SimHei) size-two headings, official-document margins)
"""

import argparse
import html
import io
import math
import re
import sys
import urllib.request
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

# ── font constants ──────────────────────────────────────────────────────────

FONT_BODY = "宋体"
FONT_BODY_ASCII = "Times New Roman"
FONT_HEADING = "黑体"
FONT_HEADING_ASCII = "Arial"

# font/size config for each style: (body_cn, body_ascii, body_pt, h1_pt, h2_pt, h3_pt)
_STYLE_FONTS = {
    "general":  (FONT_BODY, FONT_BODY_ASCII, 12, 15, 14, 12),
    "resume":   (FONT_BODY, FONT_BODY_ASCII, 10, 12, 11, 10.5),
    "patent":   (FONT_BODY, FONT_BODY_ASCII, 12, 15, 14, 12),
    "official": ("仿宋",    FONT_BODY_ASCII, 16, 22, 15, 14),
}

# line-spacing config for each style
_STYLE_LINE_SPACING = {
    "general": 1.5,
    "resume": 1.15,
    "patent": 1.5,
    "official": 1.5,
}

# patent section markers: normalized H1 text → running-header text.
# Chinese uses the official wide-spaced header form; English uses the plain label.
# Lookups go through _patent_header(), which is space-insensitive (so "权 利 要 求 书"
# matches "权利要求书") and case-insensitive for English (so "# Claims" works).
_PATENT_SECTIONS = {
    "权利要求书": "权利要求书",
    "说明书": "说  明  书",
    "摘要": "摘    要",
    "claims": "Claims",
    "specification": "Specification",
    "abstract": "Abstract",
}


def _patent_header(text: str) -> "str | None":
    """Return the running-header text for a patent H1 heading, or None if it is not one.

    Recognizes both Chinese section names (`权利要求书` / `说明书` / `摘要`, ignoring internal
    spacing variants such as `权 利 要 求 书`) and English ones, case-insensitively
    (`Claims` / `Specification` / `Abstract`).
    """
    if not text:
        return None
    stripped = text.strip()
    cn_key = re.sub(r"\s+", "", stripped)          # collapse '权 利 要 求 书' → '权利要求书'
    if cn_key in _PATENT_SECTIONS:
        return _PATENT_SECTIONS[cn_key]
    en_key = stripped.lower()
    if en_key in _PATENT_SECTIONS:
        return _PATENT_SECTIONS[en_key]
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  OMML formula conversion (LaTeX → native Word OMML)
# ══════════════════════════════════════════════════════════════════════════════

_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _m_elem(tag: str) -> etree._Element:
    return etree.Element(f"{{{_M}}}{tag}", nsmap={"m": _M})


def _m_run(text: str, style: str = "i") -> etree._Element:
    """OMML text run. style: 'i'=italic variable, 'p'=upright number/operator."""
    r = _m_elem("r")
    rPr = _m_elem("rPr")
    sty = _m_elem("sty")
    sty.set(f"{{{_M}}}val", style)
    rPr.append(sty)
    r.append(rPr)
    t = _m_elem("t")
    t.text = text
    if text and (text[0] == " " or text[-1] == " "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r


def _mml_to_omml(node: etree._Element, target: etree._Element):
    """Recursively convert a MathML node to OMML, appending to target."""
    local = etree.QName(node.tag).localname

    if local in ("math", "mrow", "mstyle"):
        for child in node:
            _mml_to_omml(child, target)
    elif local == "mi":
        text = node.text or ""
        target.append(_m_run(text, "i" if len(text) == 1 else "p"))
    elif local == "mn":
        target.append(_m_run(node.text or "", "p"))
    elif local == "mo":
        target.append(_m_run(node.text or "", "p"))
    elif local == "mtext":
        target.append(_m_run(node.text or "", "p"))
    elif local == "mfrac":
        children = list(node)
        f = _m_elem("f")
        if len(children) >= 2:
            num = _m_elem("num")
            _mml_to_omml(children[0], num)
            den = _m_elem("den")
            _mml_to_omml(children[1], den)
            f.append(num)
            f.append(den)
        target.append(f)
    elif local == "msup":
        children = list(node)
        ssup = _m_elem("sSup")
        if len(children) >= 2:
            e = _m_elem("e")
            _mml_to_omml(children[0], e)
            sup = _m_elem("sup")
            _mml_to_omml(children[1], sup)
            ssup.append(e)
            ssup.append(sup)
        target.append(ssup)
    elif local == "msub":
        children = list(node)
        ssub = _m_elem("sSub")
        if len(children) >= 2:
            e = _m_elem("e")
            _mml_to_omml(children[0], e)
            sub = _m_elem("sub")
            _mml_to_omml(children[1], sub)
            ssub.append(e)
            ssub.append(sub)
        target.append(ssub)
    elif local == "msubsup":
        children = list(node)
        ssubsup = _m_elem("sSubSup")
        if len(children) >= 3:
            e = _m_elem("e")
            _mml_to_omml(children[0], e)
            sub = _m_elem("sub")
            _mml_to_omml(children[1], sub)
            sup = _m_elem("sup")
            _mml_to_omml(children[2], sup)
            ssubsup.append(e)
            ssubsup.append(sub)
            ssubsup.append(sup)
        target.append(ssubsup)
    elif local == "msqrt":
        rad = _m_elem("rad")
        radPr = _m_elem("radPr")
        degHide = _m_elem("degHide")
        degHide.set(f"{{{_M}}}val", "1")
        radPr.append(degHide)
        rad.append(radPr)
        rad.append(_m_elem("deg"))
        e = _m_elem("e")
        for child in node:
            _mml_to_omml(child, e)
        rad.append(e)
        target.append(rad)
    elif local == "mroot":
        children = list(node)
        rad = _m_elem("rad")
        rad.append(_m_elem("radPr"))
        deg = _m_elem("deg")
        if len(children) >= 2:
            _mml_to_omml(children[1], deg)
        rad.append(deg)
        e = _m_elem("e")
        if children:
            _mml_to_omml(children[0], e)
        rad.append(e)
        target.append(rad)
    else:
        if node.text:
            target.append(_m_run(node.text, "p"))


def _latex_to_omml(latex: str) -> etree._Element:
    import latex2mathml.converter
    mml_root = etree.fromstring(latex2mathml.converter.convert(latex).encode())
    omath = _m_elem("oMath")
    _mml_to_omml(mml_root, omath)
    return omath


def _add_inline_omml(para, latex: str):
    """Append an inline OMML formula to the paragraph (LaTeX → native Word math formula)."""
    para._p.append(_latex_to_omml(latex))


# ══════════════════════════════════════════════════════════════════════════════
#  Markdown parsing
# ══════════════════════════════════════════════════════════════════════════════

def _is_special(line: str) -> bool:
    """Determine whether a line is a special line (heading/list/table/code fence/separator/image/formula block), used for merging multi-line paragraphs."""
    s = line.strip()
    if not s:
        return True
    if re.match(r'^#{1,4}\s', s):
        return True
    if re.match(r'^[-*]\s', s):
        return True
    if re.match(r'^\d+\.\s', s):
        return True
    if s.startswith('|'):
        return True
    if s.startswith('```'):
        return True
    if re.match(r'^---+$', s):
        return True
    if re.match(r'^!\[', s):
        return True
    if s.startswith('$$'):
        return True
    return False


def parse_markdown(text: str) -> list[dict]:
    """
    Parse Markdown text into a list of document elements.
    Element types: heading, paragraph, unordered_list, ordered_list,
              table, code_block, page_break, formula_block
    """
    elements: list[dict] = []
    lines = text.split('\n')
    n = len(lines)
    i = 0

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # ── code block ───
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            elements.append({'type': 'code_block', 'code': '\n'.join(code_lines), 'lang': lang})
            continue

        # ── standalone formula block: $$...$$ (single line) or multi-line block ───
        if stripped.startswith('$$'):
            # single line: $$latex$$ or $$latex$$ (4-3)
            m_single = re.match(r'^\$\$(.+?)\$\$\s*(\([^)]+\))?\s*$', stripped)
            if m_single:
                elements.append({
                    'type': 'formula_block',
                    'latex': m_single.group(1).strip(),
                    'label': m_single.group(2) or '',
                })
                i += 1
                continue
            # multi-line: starts with $$ on its own line, ends with $$ or $$ (label)
            if stripped == '$$':
                formula_lines: list[str] = []
                label = ''
                i += 1
                while i < n and not lines[i].strip().startswith('$$'):
                    formula_lines.append(lines[i])
                    i += 1
                if i < n:
                    label_m = re.match(r'^\$\$\s*(\([^)]+\))\s*$', lines[i].strip())
                    label = label_m.group(1) if label_m else ''
                    i += 1
                elements.append({
                    'type': 'formula_block',
                    'latex': '\n'.join(formula_lines).strip(),
                    'label': label,
                })
                continue
            # other lines starting with $$ but not matching the formats above: treat as an ordinary paragraph
            elements.append({'type': 'paragraph', 'text': stripped})
            i += 1
            continue

        # ── heading ───
        m = re.match(r'^(#{1,4})\s+(.+)$', stripped)
        if m:
            elements.append({'type': 'heading', 'level': len(m.group(1)), 'text': m.group(2).strip()})
            i += 1
            continue

        # ── separator ───
        if re.match(r'^---+$', stripped):
            elements.append({'type': 'page_break'})
            i += 1
            continue

        # ── image ───
        m_img = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', stripped)
        if m_img:
            elements.append({'type': 'image', 'alt': m_img.group(1).strip(), 'url': m_img.group(2).strip()})
            i += 1
            continue

        # ── table ───
        if stripped.startswith('|'):
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith('|'):
                row_text = lines[i].strip()
                if re.match(r'^\|[\s\-:|]+\|$', row_text):
                    i += 1
                    continue
                cells = [c.strip() for c in row_text.split('|')[1:-1]]
                rows.append(cells)
                i += 1
            if rows:
                elements.append({'type': 'table', 'headers': rows[0], 'rows': rows[1:]})
            continue

        # ── unordered list (supports multi-line continuation) ───
        if re.match(r'^[-*]\s+', stripped):
            items: list[str] = []
            while i < n:
                line_i = lines[i].strip()
                if not line_i:
                    # blank line: check whether more list items of the same kind follow; if so, skip the blank line and keep collecting
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and re.match(r'^[-*]\s+', lines[j].strip()):
                        i = j
                        continue
                    break
                if re.match(r'^[-*]\s+', line_i):
                    item_text = re.sub(r'^[-*]\s+', '', line_i)
                    i += 1
                    while i < n and lines[i].strip() and not _is_special(lines[i]):
                        item_text += lines[i].strip()
                        i += 1
                    items.append(item_text)
                else:
                    break
            elements.append({'type': 'unordered_list', 'items': items})
            continue

        # ── ordered list (supports blank-line separation + multi-line continuation, avoiding a separate number per item) ───
        if re.match(r'^\d+\.\s+', stripped):
            items_ol: list[str] = []
            while i < n:
                line_i = lines[i].strip()
                if not line_i:
                    # blank line: check whether more numbered items follow; if so, skip the blank line and keep collecting
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and re.match(r'^\d+\.\s+', lines[j].strip()):
                        i = j
                        continue
                    break
                if re.match(r'^\d+\.\s+', line_i):
                    item_text = re.sub(r'^\d+\.\s+', '', line_i)
                    i += 1
                    # collect non-special continuation lines (multi-line text belonging to the same list item)
                    while i < n and lines[i].strip() and not _is_special(lines[i]):
                        item_text += lines[i].strip()
                        i += 1
                    items_ol.append(item_text)
                else:
                    break
            elements.append({'type': 'ordered_list', 'items': items_ol})
            continue

        # ── ordinary paragraph (merge consecutive non-special lines) ───
        para_parts: list[str] = []
        while i < n and lines[i].strip() and not _is_special(lines[i]):
            para_parts.append(lines[i].strip())
            i += 1
        elements.append({'type': 'paragraph', 'text': ' '.join(para_parts)})

    return elements


# ══════════════════════════════════════════════════════════════════════════════
#  image download
# ══════════════════════════════════════════════════════════════════════════════

def _download_image(url: str) -> bytes | None:
    """Download a remote image and return the bytes; read a local path directly; return None on failure."""
    if url.startswith(('http://', 'https://')):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    return Path(url).read_bytes()


# ══════════════════════════════════════════════════════════════════════════════
#  Word low-level utilities
# ══════════════════════════════════════════════════════════════════════════════

def _set_font(run, cn=FONT_BODY, ascii_=FONT_BODY_ASCII, size=None, bold=False, italic=False):
    if size is None:
        size = Pt(12)
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = ascii_
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._element.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        run._element.insert(0, rPr)
    # clear Word theme-color attributes to ensure the explicit black is not overridden by the theme
    color_el = rPr.find(qn('w:color'))
    if color_el is not None:
        for attr in (qn('w:themeColor'), qn('w:themeTint'), qn('w:themeShade')):
            color_el.attrib.pop(attr, None)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), cn)
    rFonts.set(qn('w:ascii'), ascii_)
    rFonts.set(qn('w:hAnsi'), ascii_)


def _setup_page(section, style="general"):
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    if style == "official":
        section.top_margin = Cm(3.7)
        section.bottom_margin = Cm(3.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.6)
    elif style == "resume":
        for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
            setattr(section, attr, Cm(1.8))
    else:
        for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
            setattr(section, attr, Cm(2.5))


def _set_header(section, text):
    h = section.header
    h.is_linked_to_previous = False
    p = h.paragraphs[0] if h.paragraphs else h.add_paragraph()
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_font(p.add_run(text), FONT_HEADING, FONT_HEADING_ASCII, Pt(10.5))


def _set_footer(section):
    f = section.footer
    f.is_linked_to_previous = False
    p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_font(p.add_run("Page "), size=Pt(9))
    fld = OxmlElement('w:fldChar'); fld.set(qn('w:fldCharType'), 'begin')
    p.add_run()._element.append(fld)
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = ' PAGE '
    p.add_run()._element.append(instr)
    fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'), 'end')
    p.add_run()._element.append(fld2)


def _para_bg(para, hex_color: str):
    """Full-line paragraph background color."""
    pPr = para._p.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        para._p.insert(0, pPr)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)


def _code_run(para, text: str, size_pt: int = 9, color: str = "2B2B2B"):
    run = para.add_run(text)
    run.font.size = Pt(size_pt)
    rPr = run._element.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        run._element.insert(0, rPr)
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia"):
        rFonts.set(qn(attr), "Courier New")
    clr = rPr.find(qn("w:color"))
    if clr is None:
        clr = OxmlElement("w:color")
        rPr.append(clr)
    clr.set(qn("w:val"), color)


# ── prose sanitization ────────────────────────────────────────────────────────
# Models often emit HTML tags / entities (<br>, <center>, &nbsp;) or stray Markdown
# into the source text. Left untouched these survive verbatim in the .docx and look
# broken. We sanitize prose text (headings / paragraphs / list items / table cells)
# BEFORE inline parsing. Code blocks and $$formula$$ blocks are rendered by other
# paths and are never passed through here, so their literal characters are preserved.

# Exact, attribute-less inline tags → drop the tag, keep inner text.
_HTML_TAGS_EXACT = re.compile(
    r'</?(?:b|i|u|em|strong|sub|sup|mark|small|s|strike|del|ins|code|tt|big)>', re.I
)
# Tags that commonly carry attributes → drop the whole tag, keep inner text. The
# tag name is anchored so ordinary prose like "a < b and c > d" is NOT matched.
_HTML_TAGS_BLOCK = re.compile(
    r'</?(?:center|span|div|font|p|section|article|blockquote|h[1-6]|ul|ol|li|a|pre|figure|figcaption|table|thead|tbody|tr|td|th)\b[^>]*>',
    re.I,
)
_BR_TAG = re.compile(r'<br\s*/?>', re.I)


def _sanitize_prose(text: str) -> str:
    """Strip HTML artifacts from prose so they never leak into the document.

    - decodes HTML entities (&nbsp; &amp; &lt; …, plus numeric) and normalizes the
      non-breaking space to a regular space
    - converts <br> / <br/> to a newline (rendered as an in-paragraph line break)
    - removes known HTML tags while keeping their inner text
    """
    if not text:
        return text
    text = html.unescape(text)
    text = text.replace('\xa0', ' ')
    text = _BR_TAG.sub('\n', text)
    text = _HTML_TAGS_EXACT.sub('', text)
    text = _HTML_TAGS_BLOCK.sub('', text)
    return text


def _balance_bold(text: str) -> str:
    """Drop unbalanced ``**`` markers so they neither leak as literal text nor mis-pair.

    An odd / mismatched number of ``**`` (malformed or unclosed bold) otherwise makes
    ``_parse_inline`` greedily pair the wrong markers — bolding the wrong span and leaking
    the inner markup (e.g. a stray ``conversion**`` swallowing a following ``**word**``).
    We pair markers with a whitespace-flanking stack and remove any that stay unmatched,
    leaving only well-formed ``**bold**`` pairs for ``_parse_inline``.
    """
    positions = [m.start() for m in re.finditer(r'\*\*', text)]
    if not positions:
        return text

    def can_open(pos):
        nxt = text[pos + 2] if pos + 2 < len(text) else ''
        return nxt != '' and not nxt.isspace()

    def can_close(pos):
        prv = text[pos - 1] if pos - 1 >= 0 else ''
        return prv != '' and not prv.isspace()

    keep = set()
    stack = []
    for pos in positions:
        if can_close(pos) and stack:
            keep.add(stack.pop())
            keep.add(pos)
        elif can_open(pos):
            stack.append(pos)
        # otherwise: dangling marker → dropped

    if len(keep) == len(positions):
        return text

    pos_set = set(positions)
    out = []
    i = 0
    n = len(text)
    while i < n:
        if i in pos_set and text[i:i + 2] == '**':
            if i in keep:
                out.append('**')
            i += 2
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)


def _parse_inline(text: str) -> list[tuple[str, str]]:
    """
    Parse inline markup, returning [(text, kind), ...].
    kind: 'normal' | 'bold' | 'italic' | 'formula'
    Supports: **bold**, *italic*, $inline formula$ (LaTeX syntax)
    """
    parts: list[tuple[str, str]] = []
    # Order matters: **bold** first, then $formula$, then a conservative *italic*.
    # The italic arm requires the '*' to sit on a word/space boundary and to hug
    # non-space content, so "3 * 4", "a*b", and "**bold**" are NOT treated as italic.
    pattern = re.compile(
        r'\*\*(?P<bold>.+?)\*\*'
        r'|\$(?P<formula>[^$\n]+?)\$'
        r'|(?<![\*\w])\*(?!\s)(?P<italic>[^*\n]+?)(?<!\s)\*(?![\*\w])'
    )
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            parts.append((text[last:m.start()], 'normal'))
        if m.group('bold') is not None:
            parts.append((m.group('bold'), 'bold'))
        elif m.group('formula') is not None:
            parts.append((m.group('formula'), 'formula'))
        else:
            parts.append((m.group('italic'), 'italic'))
        last = m.end()
    if last < len(text):
        parts.append((text[last:], 'normal'))
    return parts or [(text, 'normal')]


def _render_runs(para, text: str, cn: str, ascii_: str, size_pt: int):
    """
    Render text containing **bold** / *italic* / $formula$ markup as paragraph runs,
    after sanitizing HTML artifacts. The formula segment is rendered as an inline OMML
    formula; a newline (from a <br>) becomes an in-paragraph line break.
    """
    text = _balance_bold(_sanitize_prose(text))
    for chunk, kind in _parse_inline(text):
        if not chunk:
            continue
        if kind == 'formula':
            _add_inline_omml(para, chunk)
            continue
        segments = chunk.split('\n')
        for si, seg in enumerate(segments):
            if si > 0:
                para.add_run().add_break()
            if seg:
                _set_font(para.add_run(seg), cn, ascii_, Pt(size_pt),
                          bold=(kind == 'bold'), italic=(kind == 'italic'))


# ══════════════════════════════════════════════════════════════════════════════
#  element rendering
# ══════════════════════════════════════════════════════════════════════════════

def _render_heading(doc, el: dict, style: str):
    level = el['level']
    text = el['text']
    _, _, _, h1, h2, h3 = _STYLE_FONTS[style]
    size_map = {1: h1, 2: h2, 3: h3, 4: h3}
    line_sp = _STYLE_LINE_SPACING.get(style, 1.5)

    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = line_sp
    pf.keep_with_next = True
    pf.widow_control = True

    if style == "resume":
        pf.space_before = Pt(6)
        pf.space_after = Pt(2)
    else:
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        if level == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    _render_runs(p, text, FONT_HEADING, FONT_HEADING_ASCII, size_map.get(level, h3))


def _first_line_indent_2char(body_pt: float) -> Pt:
    """Compute a first-line indent of 2 Chinese-character widths (= 2 × font size)."""
    return Pt(body_pt * 2)


def _render_paragraph(doc, el: dict, style: str):
    body_cn, body_ascii, body_pt, *_ = _STYLE_FONTS[style]
    line_sp = _STYLE_LINE_SPACING.get(style, 1.5)
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = line_sp
    pf.space_before = Pt(0)
    pf.widow_control = True

    if style == "resume":
        pf.space_after = Pt(2)
    else:
        pf.space_after = Pt(6)
        pf.first_line_indent = _first_line_indent_2char(body_pt)

    # A paragraph fully wrapped in <center>...</center> is centered (the tags
    # themselves are stripped by _sanitize_prose inside _render_runs).
    if re.match(r'^\s*<center>.*</center>\s*$', el['text'], re.I | re.S):
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.first_line_indent = Pt(0)

    _render_runs(p, el['text'], body_cn, body_ascii, body_pt)


def _render_unordered_list(doc, el: dict, style: str):
    body_cn, body_ascii, body_pt, *_ = _STYLE_FONTS[style]
    line_sp = _STYLE_LINE_SPACING.get(style, 1.5)
    hang = Cm(0.5)
    base_indent = Cm(0) if style == "resume" else Cm(0.74)
    for item in el['items']:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = line_sp
        pf.space_after = Pt(1) if style == "resume" else Pt(2)
        pf.left_indent = base_indent + hang
        pf.first_line_indent = -hang
        p.add_run("• ")
        _render_runs(p, item, body_cn, body_ascii, body_pt)


def _render_ordered_list(doc, el: dict, style: str, patent_claims: bool = False):
    body_cn, body_ascii, body_pt, *_ = _STYLE_FONTS[style]
    line_sp = _STYLE_LINE_SPACING.get(style, 1.5)
    # hanging-indent width: leave enough room for a number like "10. "
    hang = Cm(1.0)
    for idx, item in enumerate(el['items'], 1):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = line_sp
        pf.space_after = Pt(1) if style == "resume" else Pt(6)
        # patent claims: independent/dependent claims all indented at the same level, per CNIPA convention
        pf.left_indent = Cm(0) if style == "resume" else hang
        pf.first_line_indent = -hang

        num_run = p.add_run(f"{idx}. ")
        _set_font(num_run, body_cn, body_ascii, Pt(body_pt), bold=patent_claims)
        _render_runs(p, item, body_cn, body_ascii, body_pt)


def _render_table(doc, el: dict, style: str):
    headers = el['headers']
    rows = el.get('rows', [])
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'

    for ci, h in enumerate(headers):
        cell = table.rows[0].cells[ci]
        cell.text = ""
        header_text = _sanitize_prose(str(h)).replace("\n", " ")
        _set_font(cell.paragraphs[0].add_run(header_text), FONT_HEADING, FONT_HEADING_ASCII, Pt(11), bold=True)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            if ci < len(table.columns):
                cell = table.rows[ri + 1].cells[ci]
                cell.text = ""
                # Route through _render_runs so cell text is sanitized and supports
                # **bold** / *italic* / $formula$ instead of leaking raw markup.
                _render_runs(cell.paragraphs[0], str(val), FONT_BODY, FONT_BODY_ASCII, 11)


def _render_code_block(doc, el: dict):
    code = el['code']
    lang = el.get('lang', '')
    code_lines = code.split('\n')
    while code_lines and not code_lines[0].strip():
        code_lines.pop(0)
    while code_lines and not code_lines[-1].strip():
        code_lines.pop()

    lp = doc.add_paragraph()
    _para_bg(lp, "F2F2F2")
    lp.paragraph_format.space_before = Pt(6)
    lp.paragraph_format.space_after = Pt(2)
    lp.paragraph_format.left_indent = Cm(0.4)
    lr = lp.add_run(f"Code block  {lang}" if lang else "Code block")
    lr.font.size = Pt(9)
    lr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    for line in code_lines:
        p = doc.add_paragraph()
        _para_bg(p, "F2F2F2")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.4)
        _code_run(p, line)

    if code_lines:
        p.paragraph_format.space_after = Pt(6)


def _extract_tag(latex: str) -> tuple[str, str]:
    """
    Extract and remove \\tag{...} from the LaTeX string, returning (cleaned_latex, label).
    label is formatted as "(content)"; if there is no \\tag, label is an empty string.
    """
    m = re.search(r'\\tag\{([^}]+)\}', latex)
    if m:
        label = f"({m.group(1)})"
        cleaned = (latex[:m.start()] + latex[m.end():]).strip()
        return cleaned, label
    return latex, ''


def _render_formula_block(doc, el: dict):
    """
    Render a $$...$$ standalone formula block as a centered Word OMML formula, with an optional number label.
    Corresponding Markdown syntax:
        $$\\frac{a}{b}$$            (no label)
        $$\\frac{a}{b}$$ (4-3)     (end-of-line parenthetical label)
        $$\\frac{a}{b} \\tag{4-3}$$ (LaTeX \\tag label, extracted automatically)
    """
    latex = el['latex']
    label = el.get('label', '')
    # \\tag{...} takes priority over an end-of-line parenthetical label
    latex, tag_label = _extract_tag(latex)
    if tag_label:
        label = tag_label
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para._p.append(_latex_to_omml(latex))
    if label:
        run = para.add_run(f"    {label}")
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)


def _render_image(doc, el: dict, style: str):
    """
    Insert an image and its caption (the caption goes below the image, centered).
    The image must be downloaded from the URL first; directly referencing an image-host link is not supported.
    Width is limited to 14 cm by default; local paths are also supported.
    """
    url = el['url']
    alt = el.get('alt', '')

    image_data = _download_image(url)
    if image_data is None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"[Image failed to load: {alt or url}]")
        r.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        return

    pic_para = doc.add_paragraph()
    pic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic_para.paragraph_format.space_before = Pt(6)
    pic_para.paragraph_format.space_after = Pt(2)
    pic_para.add_run().add_picture(io.BytesIO(image_data), width=Cm(14))

    if alt:
        body_cn, body_ascii, body_pt, *_ = _STYLE_FONTS[style]
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(0)
        cap.paragraph_format.space_after = Pt(12)
        _set_font(cap.add_run(alt), body_cn, body_ascii, Pt(body_pt - 1))


# ══════════════════════════════════════════════════════════════════════════════
#  mode dispatch
# ══════════════════════════════════════════════════════════════════════════════

def _render_general(doc, elements: list[dict], style: str):
    """Rendering for the general / official-document / resume modes."""
    sec0 = doc.sections[0]
    _setup_page(sec0, style)
    if style != "resume":
        _set_footer(sec0)

    for el in elements:
        t = el['type']
        if t == 'heading':
            _render_heading(doc, el, style)
        elif t == 'paragraph':
            _render_paragraph(doc, el, style)
        elif t == 'unordered_list':
            _render_unordered_list(doc, el, style)
        elif t == 'ordered_list':
            _render_ordered_list(doc, el, style)
        elif t == 'table':
            _render_table(doc, el, style)
        elif t == 'code_block':
            _render_code_block(doc, el)
        elif t == 'formula_block':
            _render_formula_block(doc, el)
        elif t == 'image':
            _render_image(doc, el, style)
        elif t == 'page_break':
            # in general/official mode, --- is only a visual separator and does not force a page break
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)


def _render_patent(doc, elements: list[dict]):
    """
    Patent mode: detect the Claims/Specification/Abstract H1 headings — either English
    (`# Claims` / `# Specification` / `# Abstract`) or Chinese (`权利要求书` / `说明书` / `摘要`) —
    and automatically split into independent Word Sections (each with its own header and page numbers).
    Ordered lists under the claims are rendered in patent-entry format.
    """
    style = "patent"
    sec0 = doc.sections[0]
    _setup_page(sec0, style)

    current_section_name = None
    first_section = True
    in_claims = False

    for el in elements:
        t = el['type']

        # H1 triggers a patent section break
        if t == 'heading' and el['level'] == 1:
            header_text = _patent_header(el['text'])
            if header_text:
                if not first_section:
                    sec = doc.add_section()
                    _setup_page(sec, style)
                else:
                    sec = sec0
                    first_section = False
                _set_header(sec, header_text)
                _set_footer(sec)
                current_section_name = el['text']
                in_claims = ("权利要求" in el['text']) or ("claim" in el['text'].lower())
                _render_heading(doc, el, style)
                continue

        # in patent mode, page_break also triggers a new section
        if t == 'page_break':
            if not first_section:
                sec = doc.add_section()
                _setup_page(sec, style)
                _set_footer(sec)
            continue

        # when the first element is not a patent section heading, initialize the default section
        if first_section:
            _set_footer(sec0)
            first_section = False

        if t == 'heading':
            _render_heading(doc, el, style)
        elif t == 'paragraph':
            _render_paragraph(doc, el, style)
        elif t == 'unordered_list':
            _render_unordered_list(doc, el, style)
        elif t == 'ordered_list':
            _render_ordered_list(doc, el, style, patent_claims=in_claims)
        elif t == 'table':
            _render_table(doc, el, style)
        elif t == 'code_block':
            _render_code_block(doc, el)
        elif t == 'formula_block':
            _render_formula_block(doc, el)
        elif t == 'image':
            _render_image(doc, el, style)


# ══════════════════════════════════════════════════════════════════════════════
#  length measurement (word / character count + page estimate)
# ══════════════════════════════════════════════════════════════════════════════

# CJK ideographs + Japanese kana + Korean hangul syllables
_CJK_RE = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]')
# scripts written without spaces between words (Thai, Lao, Myanmar, Khmer)
_NOSPACE_RE = re.compile(r'[\u0e00-\u0eff\u1000-\u109f\u1780-\u17ff]')
# a "word" token must contain a letter/digit from a space-delimited script
_WORDISH_RE = re.compile(r'[0-9A-Za-z\u00c0-\u024f\u0370-\u03ff\u0400-\u04ff]')

# Rough words- / characters-per-page by style (A4). Tables, images, headings and
# whitespace all reduce these, so they are ESTIMATES ONLY — for an exact page count
# render the .docx to PDF (scripts/docx_to_pdf.py) and count.
_WORDS_PER_PAGE = {"general": 400, "patent": 400, "resume": 550, "official": 350}
_CJK_PER_PAGE = {"general": 750, "patent": 750, "resume": 1000, "official": 620}


def _collect_doc_text(doc) -> str:
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def _measure(text: str) -> dict:
    """Language-aware length: words for space-delimited scripts, characters for CJK/Thai."""
    cjk = len(_CJK_RE.findall(text))
    nospace = len(_NOSPACE_RE.findall(text))
    words = sum(1 for tok in text.split() if _WORDISH_RE.search(tok))
    chars_no_ws = len(re.sub(r"\s+", "", text))
    return {"words": words, "cjk": cjk, "nospace": nospace, "chars": chars_no_ws}


def _estimate_pages(m: dict, style: str) -> float:
    wpp = _WORDS_PER_PAGE.get(style, 400)
    cpp = _CJK_PER_PAGE.get(style, 750)
    script_chars = m["cjk"] + m["nospace"]
    # use the character estimate when the document is predominantly non-space script
    return script_chars / cpp if script_chars > m["words"] else m["words"] / wpp


def _length_report(doc, style, target_words=None, target_chars=None,
                   target_pages=None, tolerance=0.1) -> None:
    """Print a length report (+ optional target checks) so the caller can self-correct."""
    m = _measure(_collect_doc_text(doc))
    pages_ceil = max(1, math.ceil(_estimate_pages(m, style)))

    print(f"Length: {m['words']:,} words | {m['chars']:,} non-space chars "
          f"(CJK/kana/hangul: {m['cjk']:,})")
    print(f"Estimated length: ~{pages_ceil} page(s) [{style}] — rough estimate; "
          f"render to PDF (docx_to_pdf.py) for an exact page count")

    warnings = []

    def _check(label, actual, target):
        if target is None:
            return
        lo, hi = target * (1 - tolerance), target * (1 + tolerance)
        if actual < lo or actual > hi:
            pct = (actual - target) / target * 100 if target else 0
            warnings.append(
                f"LENGTH WARNING: {label} = {actual:,} vs target {target:,} "
                f"({pct:+.0f}%, allowed +/-{int(tolerance*100)}%) — revise and regenerate"
            )
        else:
            print(f"LENGTH OK: {label} = {actual:,} within +/-{int(tolerance*100)}% of {target:,}")

    _check("words", m["words"], target_words)
    _check("chars", m["chars"], target_chars)
    if target_pages is not None:
        if pages_ceil != target_pages:
            warnings.append(
                f"LENGTH WARNING: estimated ~{pages_ceil} page(s) vs target {target_pages} "
                f"(estimate; confirm by rendering to PDF) — adjust content length"
            )
        else:
            print(f"LENGTH OK: estimated ~{pages_ceil} page(s) matches target {target_pages}")

    for w in warnings:
        print(w, file=sys.stderr)


# ══════════════════════════════════════════════════════════════════════════════
#  entry point
# ══════════════════════════════════════════════════════════════════════════════

def create(content_path: str, output_path: str, style: str = "general",
           target_words: int = None, target_chars: int = None,
           target_pages: int = None, tolerance: float = 0.1) -> None:
    text = Path(content_path).read_text(encoding="utf-8")
    elements = parse_markdown(text)

    if not elements:
        print("Error: no content was parsed", file=sys.stderr)
        sys.exit(1)

    doc = Document()
    if style == "patent":
        _render_patent(doc, elements)
    else:
        _render_general(doc, elements, style)

    doc.save(output_path)
    kb = Path(output_path).stat().st_size / 1024
    print(f"Generated: {output_path} ({kb:.1f} KB, style: {style})")
    _length_report(doc, style, target_words, target_chars, target_pages, tolerance)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a standard-typography .docx document from Markdown text",
    )
    parser.add_argument("content", help="Markdown text file (.md / .txt)")
    parser.add_argument("output", help="output .docx file path")
    parser.add_argument(
        "--style",
        choices=["general", "resume", "patent", "official"],
        default="general",
        help="typography style: general, resume (compact resume), patent (patent sections), official (official document GB/T 9704)",
    )
    parser.add_argument("--target-words", type=int, default=None,
                        help="expected word count; warns if the output is outside tolerance")
    parser.add_argument("--target-chars", type=int, default=None,
                        help="expected non-space character count (use for CJK / Thai / no-space scripts)")
    parser.add_argument("--target-pages", type=int, default=None,
                        help="expected page count (estimate only; verify by rendering to PDF)")
    parser.add_argument("--tolerance", type=float, default=0.1,
                        help="allowed deviation for word/char targets (default 0.1 = +/-10%%)")
    args = parser.parse_args()

    if not Path(args.content).exists():
        print(f"Error: file does not exist: {args.content}", file=sys.stderr)
        sys.exit(1)

    create(args.content, args.output, args.style,
           args.target_words, args.target_chars, args.target_pages, args.tolerance)


if __name__ == "__main__":
    main()
