# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Word document unpack/pack/replace tool: modify content in a .docx while preserving the original formatting.

Usage:
    # unpack: extract the .docx into an editable XML directory
    uv run scripts/docx_edit.py unpack template.docx unpacked/

    # pack: repack the edited XML directory back into a .docx
    uv run scripts/docx_edit.py pack unpacked/ output.docx

    # replace: do text replacement directly in the .docx (unpack → replace → pack in one step)
    uv run scripts/docx_edit.py replace source.docx output.docx replacements.json

On unpack, adjacent <w:r> runs with identical formatting in document.xml are merged
(and proofErr / rsid noise is stripped) so text is contiguous and easy to find/replace.
On pack, <w:t> nodes with leading/trailing whitespace are auto-repaired with
xml:space="preserve" before the XML is condensed and re-zipped.

After unpacking, use the editing tools to replace text in unpacked/word/document.xml,
leaving <w:rPr> (the formatting properties) untouched and changing only the text inside <w:t>.

replacements.json format:
    {
      "replacements": [
        {"find": "{{invention title}}", "replace": "An intelligent parking management method"},
        {"find": "old text", "replace": "new text"}
      ],
      "track_changes": false,
      "author": "assistant"
    }

When track_changes is true, the replacement is expressed as track changes, making it easy for examiners to compare.
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
import xml.dom.minidom
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SMART_QUOTES = {
    "\u201c": "&#x201C;",
    "\u201d": "&#x201D;",
    "\u2018": "&#x2018;",
    "\u2019": "&#x2019;",
}


# ──────────────────────────────────────────────
#  unpack / pack
# ──────────────────────────────────────────────

def _pretty_print_xml(path: Path) -> None:
    try:
        raw = path.read_bytes()
        dom = xml.dom.minidom.parseString(raw)
        path.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))
    except Exception:
        pass


def _escape_smart_quotes(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
        for char, entity in SMART_QUOTES.items():
            text = text.replace(char, entity)
        path.write_text(text, encoding="utf-8")
    except Exception:
        pass


def _condense_xml(path: Path) -> None:
    try:
        raw = path.read_bytes()
        dom = xml.dom.minidom.parseString(raw)
        for elem in dom.getElementsByTagName("*"):
            if elem.tagName.endswith(":t"):
                continue
            for child in list(elem.childNodes):
                if (
                    child.nodeType == child.TEXT_NODE
                    and child.nodeValue
                    and child.nodeValue.strip() == ""
                ) or child.nodeType == child.COMMENT_NODE:
                    elem.removeChild(child)
        path.write_bytes(dom.toxml(encoding="UTF-8"))
    except Exception as e:
        print(f"Warning: error while condensing {path.name}: {e}", file=sys.stderr)


# ──────────────────────────────────────────────
#  merge runs — merge adjacent <w:r> with identical formatting to reduce XML fragmentation
#  (Word often splits a single logical string into many runs, which breaks find/replace and
#  makes manual XML editing painful; merging on unpack gives clean, contiguous text nodes)
# ──────────────────────────────────────────────

def _find_dom_elements(root, tag: str) -> list:
    results = []

    def walk(node):
        if node.nodeType == node.ELEMENT_NODE:
            name = node.localName or node.tagName
            if name == tag or name.endswith(f":{tag}"):
                results.append(node)
            for child in node.childNodes:
                walk(child)

    walk(root)
    return results


def _get_dom_child(parent, tag: str):
    for child in parent.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            name = child.localName or child.tagName
            if name == tag or name.endswith(f":{tag}"):
                return child
    return None


def _merge_runs_in(container) -> int:
    count = 0
    run = None
    for child in container.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            name = child.localName or child.tagName
            if name == "r" or name.endswith(":r"):
                run = child
                break
    if not run:
        return 0

    while run:
        nxt = run.nextSibling
        while nxt and nxt.nodeType != nxt.ELEMENT_NODE:
            nxt = nxt.nextSibling
        if nxt and ((nxt.localName or nxt.tagName) == "r" or (nxt.localName or nxt.tagName).endswith(":r")):
            rpr1 = _get_dom_child(run, "rPr")
            rpr2 = _get_dom_child(nxt, "rPr")
            same = (rpr1 is None and rpr2 is None) or (
                rpr1 is not None and rpr2 is not None and rpr1.toxml() == rpr2.toxml()
            )
            if same:
                for child in list(nxt.childNodes):
                    if child.nodeType == child.ELEMENT_NODE:
                        cname = child.localName or child.tagName
                        if cname != "rPr" and not cname.endswith(":rPr"):
                            run.appendChild(child)
                container.removeChild(nxt)
                count += 1
                continue
        # Merge multiple <w:t> within a run
        t_elems = [c for c in run.childNodes
                   if c.nodeType == c.ELEMENT_NODE
                   and ((c.localName or c.tagName) == "t" or (c.localName or c.tagName).endswith(":t"))]
        for i in range(len(t_elems) - 1, 0, -1):
            curr, prev = t_elems[i], t_elems[i - 1]
            prev_text = prev.firstChild.data if prev.firstChild else ""
            curr_text = curr.firstChild.data if curr.firstChild else ""
            merged = prev_text + curr_text
            if prev.firstChild:
                prev.firstChild.data = merged
            else:
                prev.appendChild(run.ownerDocument.createTextNode(merged))
            if merged.startswith(" ") or merged.endswith(" "):
                prev.setAttribute("xml:space", "preserve")
            run.removeChild(curr)

        nxt = run.nextSibling
        while nxt and nxt.nodeType != nxt.ELEMENT_NODE:
            nxt = nxt.nextSibling
        if nxt and ((nxt.localName or nxt.tagName) == "r" or (nxt.localName or nxt.tagName).endswith(":r")):
            run = nxt
        else:
            run = None

    return count


def _merge_runs(doc_xml: Path) -> int:
    """Merge adjacent <w:r> elements with identical formatting in document.xml."""
    if not doc_xml.exists():
        return 0
    try:
        dom = xml.dom.minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    except Exception:
        return 0

    # Remove proofErr and rsid attributes (they prevent otherwise-identical runs from merging)
    for elem in _find_dom_elements(dom.documentElement, "proofErr"):
        if elem.parentNode:
            elem.parentNode.removeChild(elem)
    for run in _find_dom_elements(dom.documentElement, "r"):
        for attr in list(run.attributes.values()):
            if "rsid" in attr.name.lower():
                run.removeAttribute(attr.name)

    containers = {run.parentNode for run in _find_dom_elements(dom.documentElement, "r")}
    count = 0
    for container in containers:
        count += _merge_runs_in(container)

    doc_xml.write_bytes(dom.toxml(encoding="UTF-8"))
    return count


def _repair_whitespace(unpacked_dir: Path) -> int:
    """Add xml:space="preserve" to any <w:t> whose text has leading/trailing whitespace."""
    repairs = 0
    for xml_file in list(unpacked_dir.rglob("*.xml")):
        try:
            dom = xml.dom.minidom.parseString(xml_file.read_text(encoding="utf-8"))
            modified = False
            for elem in dom.getElementsByTagName("*"):
                if elem.tagName.endswith(":t") and elem.firstChild:
                    text = elem.firstChild.nodeValue
                    if text and (text.startswith((" ", "\t")) or text.endswith((" ", "\t"))):
                        if elem.getAttribute("xml:space") != "preserve":
                            elem.setAttribute("xml:space", "preserve")
                            repairs += 1
                            modified = True
            if modified:
                xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
        except Exception:
            pass
    return repairs


def unpack(docx_path: str, output_dir: str) -> None:
    src = Path(docx_path)
    dst = Path(output_dir)

    if not src.exists():
        print(f"Error: file does not exist: {src}", file=sys.stderr)
        sys.exit(1)

    dst.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(src, "r") as zf:
        zf.extractall(dst)

    xml_files = list(dst.rglob("*.xml")) + list(dst.rglob("*.rels"))
    for f in xml_files:
        _pretty_print_xml(f)
        _escape_smart_quotes(f)

    merge_count = _merge_runs(dst / "word" / "document.xml")

    print(f"Unpacked: {src} → {dst} ({len(xml_files)} XML files, merged {merge_count} runs)")
    print(f"Edit the text in {dst}/word/document.xml, then run the pack command to pack it back.")


def pack(input_dir: str, output_file: str) -> None:
    src = Path(input_dir)
    dst = Path(output_file)

    if not src.is_dir():
        print(f"Error: directory does not exist: {src}", file=sys.stderr)
        sys.exit(1)

    repairs = _repair_whitespace(src)
    if repairs:
        print(f"Automatically fixed {repairs} whitespace issues")

    for pattern in ["*.xml", "*.rels"]:
        for f in src.rglob(pattern):
            _condense_xml(f)

    dst.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in src.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(src))

    print(f"Packed: {src} → {dst}")


# ──────────────────────────────────────────────
#  replace — automatic unpack → replace → pack
# ──────────────────────────────────────────────

def replace(input_path: str, output_path: str, replacements_path: str) -> None:
    inp = Path(input_path)
    out = Path(output_path)
    rep = Path(replacements_path)

    if not inp.exists():
        print(f"Error: input file does not exist: {inp}", file=sys.stderr)
        sys.exit(1)
    if not rep.exists():
        print(f"Error: replacements file does not exist: {rep}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(rep.read_text(encoding="utf-8"))
    replacements = data.get("replacements", [])
    track_changes = data.get("track_changes", False)
    author = data.get("author", "assistant")

    if not replacements:
        print("Warning: no replacement rules", file=sys.stderr)
        shutil.copy2(inp, out)
        return

    with tempfile.TemporaryDirectory() as tmp:
        unpacked = Path(tmp) / "unpacked"
        unpacked.mkdir()
        with zipfile.ZipFile(inp) as z:
            z.extractall(unpacked)

        doc_xml = unpacked / "word" / "document.xml"
        if not doc_xml.exists():
            print("Error: abnormal file structure, word/document.xml not found", file=sys.stderr)
            sys.exit(1)

        xml_content = doc_xml.read_text(encoding="utf-8")
        total_count = 0

        for rule in replacements:
            find_text = rule["find"]
            replace_text = rule["replace"]

            if track_changes:
                xml_content, count = _replace_with_tracking(
                    xml_content, find_text, replace_text, author
                )
            else:
                xml_content, count = _replace_in_xml(xml_content, find_text, replace_text)

            total_count += count
            if count > 0:
                find_preview = find_text[:30] + ("..." if len(find_text) > 30 else "")
                replace_preview = replace_text[:30] + ("..." if len(replace_text) > 30 else "")
                print(f"  replace: \"{find_preview}\" → \"{replace_preview}\" ({count} occurrences)")

        doc_xml.write_text(xml_content, encoding="utf-8")

        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in unpacked.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(unpacked))

    print(f"Done: {out} ({total_count} replacements in total)")


def _replace_in_xml(xml_content: str, find: str, replace: str) -> tuple[str, int]:
    """Replace text in the XML, handling the case where the text may be split across multiple <w:t> tags."""
    result = re.sub(
        r'(<w:t[^>]*>)(.*?)(</w:t>)',
        lambda m: m.group(1) + m.group(2).replace(find, replace) + m.group(3)
        if find in m.group(2) else m.group(0),
        xml_content, flags=re.DOTALL
    )

    count = xml_content.count(find) - result.count(find) if result != xml_content else 0
    if count > 0:
        return result, count

    return _replace_across_runs(xml_content, find, replace)


def _replace_across_runs(xml_content: str, find: str, replace: str) -> tuple[str, int]:
    """Handle the case where text is split across multiple <w:r> runs—splice all text at the paragraph level before matching and replacing."""
    count = 0
    para_pattern = re.compile(r'(<w:p[ >].*?</w:p>)', re.DOTALL)
    t_pattern = re.compile(r'(<w:t[^>]*>)(.*?)(</w:t>)', re.DOTALL)

    def process_paragraph(para_match):
        nonlocal count
        para_xml = para_match.group(0)
        t_matches = list(t_pattern.finditer(para_xml))
        if not t_matches:
            return para_xml

        full_text = "".join(m.group(2) for m in t_matches)
        if find not in full_text:
            return para_xml

        new_text = full_text.replace(find, replace)
        count += full_text.count(find)

        rebuilt = para_xml
        for i, m in enumerate(reversed(t_matches)):
            idx = len(t_matches) - 1 - i
            if idx == 0:
                rebuilt = rebuilt[:m.start(2)] + new_text + rebuilt[m.end(2):]
            else:
                rebuilt = rebuilt[:m.start(2)] + rebuilt[m.end(2):]

        return rebuilt

    return para_pattern.sub(process_paragraph, xml_content), count


def _replace_with_tracking(xml_content: str, find: str, replace: str, author: str) -> tuple[str, int]:
    """Replace text with track changes (delete old + insert new)."""
    count = 0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ids = [int(x) for x in re.findall(r'w:id="(\d+)"', xml_content)]
    next_id = max(ids) + 1 if ids else 100

    def make_tracked_replace(match):
        nonlocal count, next_id
        original_text = match.group(2)
        if find not in original_text:
            return match.group(0)

        count += original_text.count(find)
        parts = original_text.split(find)
        result_parts = []

        for i, part in enumerate(parts):
            if part:
                result_parts.append(f'{match.group(1)}{part}{match.group(3)}')
            if i < len(parts) - 1:
                del_id = next_id
                ins_id = next_id + 1
                next_id += 2
                result_parts.append(
                    f'<w:del w:id="{del_id}" w:author="{author}" w:date="{ts}">'
                    f'<w:r><w:delText>{find}</w:delText></w:r></w:del>'
                    f'<w:ins w:id="{ins_id}" w:author="{author}" w:date="{ts}">'
                    f'<w:r><w:t>{replace}</w:t></w:r></w:ins>'
                )

        return "".join(result_parts)

    t_pattern = re.compile(r'(<w:t[^>]*>)(.*?)(</w:t>)', re.DOTALL)
    result = t_pattern.sub(make_tracked_replace, xml_content)
    return result, count


# ──────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Word document unpack/pack/replace tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_unpack = sub.add_parser("unpack", help="unpack a .docx into an XML directory")
    p_unpack.add_argument("docx_file", help=".docx file path")
    p_unpack.add_argument("output_dir", help="output directory")

    p_pack = sub.add_parser("pack", help="pack an XML directory into a .docx")
    p_pack.add_argument("input_dir", help="the unpacked directory")
    p_pack.add_argument("output_file", help="output .docx file path")

    p_replace = sub.add_parser("replace", help="replace text in a .docx (preserving the original formatting)")
    p_replace.add_argument("input", help="input .docx file")
    p_replace.add_argument("output", help="output .docx file")
    p_replace.add_argument("replacements", help="replacement rules JSON file")

    args = parser.parse_args()

    if args.command == "unpack":
        unpack(args.docx_file, args.output_dir)
    elif args.command == "pack":
        pack(args.input_dir, args.output_file)
    elif args.command == "replace":
        replace(args.input, args.output, args.replacements)


if __name__ == "__main__":
    main()
