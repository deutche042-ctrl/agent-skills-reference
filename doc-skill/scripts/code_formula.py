"""
Code block and formula insertion tool. Imported and called by the various doc-skill scripts.

Public API:
    add_code_block(doc, code, lang="")         gray code block using paragraph shading (no border of any kind, Word/WPS compatible)
    add_inline_formula(para, text)              inline formula within a paragraph (Times New Roman, coordinated with the body text)
    add_latex_formula(doc, latex, label="")     LaTeX → native Word OMML formula

Dependencies: python-docx, lxml, latex2mathml
"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"

_COMMENT_PREFIXES: dict[str, tuple[str, ...]] = {
    "python": ("#",), "shell": ("#",), "bash": ("#",), "r": ("#",),
    "js": ("//",), "javascript": ("//",), "java": ("//",),
    "c": ("//",), "cpp": ("//",), "ts": ("//",), "typescript": ("//",),
    "sql": ("--",), "lua": ("--",),
    "matlab": ("%",),
}

_CODE_BG = "F2F2F2"


# ── internal helpers ──────────────────────────────────────────────────────────

def _para_bg(para, hex_color: str):
    """Full-line paragraph background color (shading covers the whole page width, unaffected by indentation, no border of any kind)."""
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
    """Add a Courier New monospace run (handles rFonts correctly, no duplicate insertion)."""
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
    rFonts.set(qn("w:ascii"), "Courier New")
    rFonts.set(qn("w:hAnsi"), "Courier New")
    rFonts.set(qn("w:eastAsia"), "Courier New")
    clr = rPr.find(qn("w:color"))
    if clr is None:
        clr = OxmlElement("w:color")
        rPr.append(clr)
    clr.set(qn("w:val"), color)
    return run


# ── code block ────────────────────────────────────────────────────────────────

def add_code_block(doc: Document, code: str, lang: str = ""):
    """
    Insert a code block with a uniform light-gray background.
    Implemented with paragraph shading, no table border of any kind, no dashed lines in either Word or WPS.
    Comment lines keep the same font and color as ordinary code lines.
    """
    lines = code.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    line_num_width = len(str(len(lines)))
    block: list = []

    # label paragraph
    lp = doc.add_paragraph()
    _para_bg(lp, _CODE_BG)
    lp.paragraph_format.space_before = Pt(6)
    lp.paragraph_format.space_after = Pt(2)
    lp.paragraph_format.left_indent = Cm(0.4)
    lr = lp.add_run(f"Code block  {lang}" if lang else "Code block")
    lr.font.size = Pt(9)
    lr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    block.append(lp)

    # code lines (comments same color and font as ordinary code)
    for i, line in enumerate(lines):
        p = doc.add_paragraph()
        _para_bg(p, _CODE_BG)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.4)
        _code_run(p, f"{str(i + 1).rjust(line_num_width)}   ", color="BBBBBB")
        _code_run(p, line)
        block.append(p)

    block[-1].paragraph_format.space_after = Pt(6)
    doc.add_paragraph()


# ── inline formula ──────────────────────────────────────────────────────────

def add_inline_formula(para, text: str):
    """
    Append formula text to an existing paragraph.
    Times New Roman italic, inherits the paragraph size, naturally coordinated with the surrounding Chinese body text.
    Usage:
        p = doc.add_paragraph("The variance is ")
        add_inline_formula(p, "σ²")
        p.add_run(", where k is the convolution kernel dimension.")
    """
    run = para.add_run(text)
    run.font.italic = True
    rPr = run._element.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        run._element.insert(0, rPr)
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    # set only the Latin font, leave eastAsia empty so Chinese characters follow the document default
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    return run


# ── LaTeX → OMML formula ──────────────────────────────────────────────────────

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


def _extract_tag(latex: str) -> tuple[str, str]:
    """Extract and remove \\tag{...} from the LaTeX, returning (cleaned_latex, label)."""
    import re
    m = re.search(r'\\tag\{([^}]+)\}', latex)
    if m:
        label = f"({m.group(1)})"
        cleaned = (latex[:m.start()] + latex[m.end():]).strip()
        return cleaned, label
    return latex, ''


def add_latex_formula(doc: Document, latex: str, label: str = ""):
    """
    Insert a LaTeX formula, converted to native Word OMML, supporting fractions, superscripts/subscripts, radicals, etc.
    Parameters:
        latex  - LaTeX string, e.g. r'\frac{1}{2\pi\sigma^2}';
                 if it contains \\tag{...} it is automatically extracted as the number, no need to pass label separately
        label  - formula number, e.g. "(4-9)"; \\tag takes priority over this parameter
    """
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
    doc.add_paragraph()
