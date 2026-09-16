#!/usr/bin/env python3
"""Portable static preflight checks for editable PPTX deliverables."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import posixpath
import re
import sys
import unicodedata
from typing import Any, Mapping
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

REQUIRED_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "ppt/presentation.xml",
}

PLACEHOLDER_RE = re.compile(
    r"TODO|TBD|Lorem\s+ipsum|placeholder|replace\s+me|待补|待填写|占位|示例文案",
    re.IGNORECASE,
)

SOURCE_MARKERS = ("source", "来源", "数据源", "资料来源", "资料：", "数据：")
MIN_WARN_FONT_SIZE = 900  # Legacy advisory threshold for any explicitly sized text.
MIN_BODY_FONT_PT = 10.0
AUTOFIT_REVIEW_FONT_PT = 12.0

EMU_PER_INCH = 914400
DEFAULT_FONT_PT = 18.0
LATIN_GLYPH_EM = 0.52
CJK_GLYPH_EM = 1.0
WHITESPACE_GLYPH_EM = 0.33
PUNCTUATION_GLYPH_EM = 0.35
LINE_HEIGHT_FACTOR = 1.2
OVERFLOW_TOLERANCE_IN = 0.08
OVERFLOW_RATIO = 1.10
NEAR_CAPACITY_RATIO = 0.85
COLLISION_TOLERANCE_IN = 0.03
AUTOFIT_APPROACH_IN = 0.08
FOOTER_ZONE_RATIO = 0.0667
PAGE_NUMBER_FAR_RIGHT_RATIO = 0.75
PAGE_NUMBER_CLEARANCE_IN = 0.15
ASPECT_RATIO_TOLERANCE = 0.001

PAGE_NUMBER_RE = re.compile(r"^\s*\d{1,4}(?:\s*/\s*\d{1,4})?\s*$")

TOOL_FAILURE_CODES = {"FILE_NOT_FOUND", "READ_ERROR", "INVALID_EXPECTED_ASPECT_RATIO"}
REVIEW_REQUIRED_CODES = {
    "AUTOFIT_GROWTH_RISK",
    "BODY_FONT_TOO_SMALL",
    "CHART_SOURCE_MISSING",
    "FONT_FAMILY_DRIFT",
    "OUT_OF_BOUNDS",
    "PAGE_FURNITURE_DRIFT",
    "SHAPE_TO_FIT_BODY_TEXT",
    "TEXT_LAYOUT_UNSUPPORTED",
    "TEXT_METRICS_FALLBACK",
    "TITLE_GEOMETRY_DRIFT",
    "TYPE_SCALE_DRIFT",
}
HIGH_CONFIDENCE_GEOMETRY_CODES = {
    "FOOTER_PAGE_NUMBER_COLLISION",
    "FOOTER_TEXT_OVERFLOW",
    "TABLE_FOOTER_COLLISION",
}

_DEFAULT_LEFT_RIGHT_MARGIN_EMU = round(0.1 * EMU_PER_INCH)
_DEFAULT_TOP_BOTTOM_MARGIN_EMU = round(0.05 * EMU_PER_INCH)


@dataclass(frozen=True)
class TextRun:
    """One visible run segment with its effective slide-local font metrics."""

    text: str
    font_pt: float
    font_fallback: bool


@dataclass(frozen=True)
class TextLine:
    """One explicit line, retaining styled runs for wrapping and height."""

    text: str
    runs: tuple[TextRun, ...]
    font_pt: float
    font_fallback: bool


@dataclass(frozen=True)
class TextParagraph:
    """Direct paragraph metrics retained for deterministic text estimation."""

    lines: tuple[str, ...]
    line_metrics: tuple[TextLine, ...]
    spacing_before_pt: float
    spacing_after_pt: float
    font_pt: float
    font_fallback: bool
    alignment: str


@dataclass(frozen=True)
class TextShape:
    """A supported slide-local editable text frame."""

    part: str
    slide: int
    shape_id: int | str | None
    name: str
    bounds_emu: tuple[int, int, int, int]
    margins_emu: tuple[int, int, int, int]
    text: str
    paragraphs: tuple[TextParagraph, ...]
    font_pt: float
    font_fallback: bool
    autofit: str
    font_scale: float
    line_spacing_reduction: float
    wrap: str
    vertical_anchor: str
    is_placeholder: bool


@dataclass(frozen=True)
class PageNumberMarker:
    """A short numeric footer marker and its reserved horizontal zone."""

    shape: TextShape
    position: str
    safe_left_in: float
    safe_top_in: float
    safe_right_in: float
    safe_bottom_in: float


def _add_issue(
    issues: list[dict[str, Any]],
    severity: str,
    code: str,
    message: str,
    *,
    part: str | None = None,
    slide: int | None = None,
    shape: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> None:
    item: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if part is not None:
        item["part"] = part
    if slide is not None:
        item["slide"] = slide
    if shape is not None:
        item["shape"] = dict(shape)
    if evidence is not None:
        item["evidence"] = dict(evidence)
    issues.append(item)


def _finalize_report(report: dict[str, Any]) -> dict[str, Any]:
    """Translate raw findings into V2.3 confidence-aware severities."""

    issues = report["issues"]
    code_occurrences: dict[tuple[int, str], int] = {}
    for issue in issues:
        raw_severity = issue["severity"]
        code = issue["code"]
        slide = int(issue.get("slide", 0))
        evidence = issue.get("evidence") or {}

        if code in TOOL_FAILURE_CODES:
            severity = "tool_failure"
        elif code in HIGH_CONFIDENCE_GEOMETRY_CODES:
            severity = "blocking"
        elif code == "TEXT_FRAME_OVERFLOW":
            high_confidence = (
                (
                    evidence.get("autofit") == "none"
                    or (
                        evidence.get("autofit") == "shape"
                        and float(evidence.get("utilization", 0.0)) >= 2.0
                    )
                )
                and not evidence.get("font_fallback", False)
            )
            severity = "blocking" if high_confidence else "review_required"
        elif code == "TEXT_BOX_COLLISION":
            # A material occupied-text intersection is already a semantic defect.
            # Never make a crowded or damaged slide *less* blocking merely because
            # it contains more findings.
            severity = "blocking"
        elif code == "OUT_OF_BOUNDS":
            # Text, tables, charts, and other graphic frames must stay entirely on
            # canvas.  Only non-text decorative shapes or pictures may use an
            # intentional bleed that is resolved through a design exception.
            content_bearing = bool(evidence.get("has_visible_text")) or evidence.get(
                "shape_kind"
            ) == "graphicFrame"
            severity = (
                "blocking"
                if content_bearing or evidence.get("extreme_coordinates")
                else "review_required"
            )
        elif code == "AUTOFIT_GROWTH_RISK":
            high_confidence = (
                float(evidence.get("utilization", 0.0)) > OVERFLOW_RATIO
                and not evidence.get("font_fallback", False)
                and bool(evidence.get("risks"))
            )
            severity = "blocking" if high_confidence else "review_required"
        elif code in REVIEW_REQUIRED_CODES:
            severity = "review_required"
        elif raw_severity == "error":
            severity = "blocking"
        else:
            severity = "advisory"

        issue["raw_severity"] = raw_severity
        issue["severity"] = severity
        key = (slide, code)
        code_occurrences[key] = code_occurrences.get(key, 0) + 1
        issue["id"] = f"S{slide:03d}-{code}-{code_occurrences[key]:03d}"

    severity_rank = {"tool_failure": 0, "blocking": 1, "review_required": 2, "advisory": 3}
    issues.sort(key=lambda item: (severity_rank.get(item["severity"], 9), item.get("slide", 0), item["code"]))

    summary = report["summary"]
    summary["blocking"] = sum(issue["severity"] == "blocking" for issue in issues)
    summary["review_required"] = sum(issue["severity"] == "review_required" for issue in issues)
    summary["advisories"] = sum(issue["severity"] == "advisory" for issue in issues)
    summary["tool_failures"] = sum(issue["severity"] == "tool_failure" for issue in issues)
    # Backward-compatible aliases for callers that still consume V1.2 summaries.
    summary["errors"] = summary["blocking"]
    summary["warnings"] = summary["review_required"] + summary["advisories"]
    return report


def _parse_xml(
    package: zipfile.ZipFile,
    part: str,
    issues: list[dict[str, Any]],
) -> ET.Element | None:
    try:
        payload = package.read(part)
    except KeyError:
        _add_issue(issues, "error", "MISSING_PART", f"Required XML part is missing: {part}", part=part)
        return None
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        _add_issue(issues, "error", "INVALID_XML", f"Cannot parse {part}: {exc}", part=part)
        return None


def _slide_number(part: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", part)
    return int(match.group(1)) if match else 0


def _source_part_for_relationships(rel_part: str) -> str:
    if rel_part == "_rels/.rels":
        return ""
    rel_dir = posixpath.dirname(rel_part)
    source_dir = posixpath.dirname(rel_dir)
    filename = posixpath.basename(rel_part)
    return posixpath.join(source_dir, filename[: -len(".rels")])


def _resolve_target(source_part: str, target: str) -> str:
    clean = unquote(target.split("#", 1)[0]).replace("\\", "/")
    if clean.startswith("/"):
        return posixpath.normpath(clean.lstrip("/"))
    source_dir = posixpath.dirname(source_part)
    return posixpath.normpath(posixpath.join(source_dir, clean))


def _check_relationships(
    package: zipfile.ZipFile,
    names: set[str],
    issues: list[dict[str, Any]],
) -> int:
    external_count = 0
    rel_parts = sorted(name for name in names if name.endswith(".rels"))
    for rel_part in rel_parts:
        root = _parse_xml(package, rel_part, issues)
        if root is None:
            continue
        source_part = _source_part_for_relationships(rel_part)
        for relationship in root.findall("pr:Relationship", NS):
            target = relationship.get("Target", "")
            rel_id = relationship.get("Id", "unknown")
            if not target:
                _add_issue(
                    issues,
                    "error",
                    "EMPTY_RELATIONSHIP_TARGET",
                    f"{rel_part} relationship {rel_id} has no target.",
                    part=rel_part,
                )
                continue
            if relationship.get("TargetMode", "").lower() == "external":
                external_count += 1
                _add_issue(
                    issues,
                    "warning",
                    "EXTERNAL_RELATIONSHIP",
                    f"External target may not be portable: {target}",
                    part=rel_part,
                )
                continue
            resolved = _resolve_target(source_part, target)
            if resolved not in names:
                _add_issue(
                    issues,
                    "error",
                    "BROKEN_RELATIONSHIP",
                    f"{rel_part} relationship {rel_id} points to missing part {resolved}.",
                    part=rel_part,
                )
    return external_count


def _presentation_size(
    package: zipfile.ZipFile,
    issues: list[dict[str, Any]],
) -> tuple[int, int]:
    root = _parse_xml(package, "ppt/presentation.xml", issues)
    if root is None:
        return 0, 0
    size = root.find("p:sldSz", NS)
    if size is None:
        _add_issue(issues, "error", "MISSING_SLIDE_SIZE", "ppt/presentation.xml has no p:sldSz.")
        return 0, 0
    try:
        return int(size.get("cx", "0")), int(size.get("cy", "0"))
    except ValueError:
        _add_issue(issues, "error", "INVALID_SLIDE_SIZE", "Slide width or height is not an integer.")
        return 0, 0


def _parse_aspect_ratio(value: str) -> float:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)\s*", value)
    if match is None:
        raise ValueError("aspect ratio must use W:H, for example 16:9")
    width = float(match.group(1))
    height = float(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError("aspect ratio values must be positive")
    return width / height


def _top_level_shapes(root: ET.Element) -> list[ET.Element]:
    tree = root.find("p:cSld/p:spTree", NS)
    return list(tree) if tree is not None else []


def _shape_transform(shape: ET.Element) -> ET.Element | None:
    local_name = shape.tag.rsplit("}", 1)[-1]
    if local_name in {"sp", "pic", "cxnSp"}:
        return shape.find("p:spPr/a:xfrm", NS)
    if local_name == "graphicFrame":
        return shape.find("p:xfrm", NS)
    if local_name == "grpSp":
        return shape.find("p:grpSpPr/a:xfrm", NS)
    return None


def _bounds(transform: ET.Element | None) -> tuple[int, int, int, int] | None:
    if transform is None:
        return None
    off = transform.find("a:off", NS)
    ext = transform.find("a:ext", NS)
    if off is None or ext is None:
        return None
    try:
        return (
            int(off.get("x", "0")),
            int(off.get("y", "0")),
            int(ext.get("cx", "0")),
            int(ext.get("cy", "0")),
        )
    except ValueError:
        return None


def _local_name(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def _integer_attribute(node: ET.Element, name: str, default: int) -> int:
    try:
        return int(node.get(name, str(default)))
    except ValueError:
        return default


def _shape_identity(shape: ET.Element) -> tuple[int | str | None, str]:
    identity = shape.find("p:nvSpPr/p:cNvPr", NS)
    if identity is None:
        identity = shape.find("p:nvGraphicFramePr/p:cNvPr", NS)
    if identity is None:
        identity = shape.find("p:nvGrpSpPr/p:cNvPr", NS)
    if identity is None:
        return None, ""
    raw_id = identity.get("id")
    try:
        shape_id: int | str | None = int(raw_id) if raw_id is not None else None
    except ValueError:
        shape_id = raw_id
    return shape_id, identity.get("name", "")


def _shape_is_hidden(shape: ET.Element) -> bool:
    identity = shape.find("p:nvSpPr/p:cNvPr", NS)
    if identity is None:
        identity = shape.find("p:nvGraphicFramePr/p:cNvPr", NS)
    if identity is None:
        identity = shape.find("p:nvGrpSpPr/p:cNvPr", NS)
    return identity is not None and identity.get("hidden", "").lower() in {
        "1",
        "true",
        "on",
    }


def _font_points(node: ET.Element | None) -> list[float]:
    if node is None:
        return []
    values: list[float] = []
    size = node.get("sz")
    if size:
        try:
            value = int(size)
        except ValueError:
            return values
        if value > 0:
            values.append(value / 100.0)
    return values


def _body_level_properties(text_body: ET.Element) -> dict[int, ET.Element]:
    list_style = text_body.find("a:lstStyle", NS)
    if list_style is None:
        return {}
    levels: dict[int, ET.Element] = {}
    for level in range(9):
        properties = list_style.find(f"a:lvl{level + 1}pPr", NS)
        if properties is not None:
            levels[level] = properties
    return levels


def _paragraph_level(paragraph: ET.Element) -> int:
    properties = paragraph.find("a:pPr", NS)
    if properties is None or properties.get("lvl") is None:
        return 0
    try:
        return int(properties.get("lvl", "0"))
    except ValueError:
        return -1


def _paragraph_inherited_font_point(
    paragraph: ET.Element,
    body_levels: Mapping[int, ET.Element],
) -> float | None:
    paragraph_default_points = _font_points(paragraph.find("a:pPr/a:defRPr", NS))
    if paragraph_default_points:
        return max(paragraph_default_points)
    level_properties = body_levels.get(_paragraph_level(paragraph))
    body_points = _font_points(
        level_properties.find("a:defRPr", NS) if level_properties is not None else None
    )
    return max(body_points) if body_points else None


def _paragraph_metrics(
    paragraph: ET.Element,
    body_levels: Mapping[int, ET.Element],
    font_scale: float,
) -> TextParagraph:
    inherited_font_pt = _paragraph_inherited_font_point(paragraph, body_levels)
    line_runs: list[list[TextRun]] = [[]]

    for child in paragraph:
        local_name = _local_name(child)
        if local_name == "br":
            line_runs.append([])
            continue
        if local_name not in {"r", "fld"}:
            continue
        run_points = _font_points(child.find("a:rPr", NS))
        if run_points:
            raw_font_pt = max(run_points)
            font_fallback = False
        elif inherited_font_pt is not None:
            raw_font_pt = inherited_font_pt
            font_fallback = False
        else:
            raw_font_pt = DEFAULT_FONT_PT
            font_fallback = True
        text = "".join(node.text or "" for node in child.findall(".//a:t", NS))
        segments = text.split("\n")
        for index, segment in enumerate(segments):
            if segment:
                line_runs[-1].append(
                    TextRun(
                        text=segment,
                        font_pt=raw_font_pt * font_scale,
                        font_fallback=font_fallback,
                    )
                )
            if index < len(segments) - 1:
                line_runs.append([])

    visible_runs = [run for line in line_runs for run in line]
    if inherited_font_pt is not None:
        empty_line_font_pt = inherited_font_pt * font_scale
        empty_line_fallback = False
    elif visible_runs:
        empty_line_font_pt = max(run.font_pt for run in visible_runs)
        empty_line_fallback = False
    else:
        end_points = _font_points(paragraph.find("a:endParaRPr", NS))
        if end_points:
            empty_line_font_pt = max(end_points) * font_scale
            empty_line_fallback = False
        else:
            empty_line_font_pt = DEFAULT_FONT_PT * font_scale
            empty_line_fallback = True

    lines: list[TextLine] = []
    for runs in line_runs:
        if runs:
            font_pt = max(run.font_pt for run in runs)
            font_fallback = any(run.font_fallback for run in runs)
        else:
            font_pt = empty_line_font_pt
            font_fallback = empty_line_fallback
        lines.append(
            TextLine(
                text="".join(run.text for run in runs),
                runs=tuple(runs),
                font_pt=font_pt,
                font_fallback=font_fallback,
            )
        )

    paragraph_font_pt = max(line.font_pt for line in lines)
    return TextParagraph(
        lines=tuple(line.text for line in lines),
        line_metrics=tuple(lines),
        spacing_before_pt=_paragraph_spacing_points(
            paragraph,
            "spcBef",
            paragraph_font_pt,
            body_levels,
        ),
        spacing_after_pt=_paragraph_spacing_points(
            paragraph,
            "spcAft",
            paragraph_font_pt,
            body_levels,
        ),
        font_pt=paragraph_font_pt,
        font_fallback=any(line.font_fallback for line in lines),
        alignment=_paragraph_alignment(paragraph, body_levels),
    )


def _paragraph_spacing_points(
    paragraph: ET.Element,
    element: str,
    font_pt: float,
    body_levels: Mapping[int, ET.Element],
) -> float:
    paragraph_properties = paragraph.find("a:pPr", NS)
    spacing_container = (
        paragraph_properties.find(f"a:{element}", NS)
        if paragraph_properties is not None
        else None
    )
    if spacing_container is None:
        level_properties = body_levels.get(_paragraph_level(paragraph))
        spacing_container = (
            level_properties.find(f"a:{element}", NS)
            if level_properties is not None
            else None
        )
    if spacing_container is None:
        return 0.0
    spacing = spacing_container.find("a:spcPts", NS)
    if spacing is not None:
        try:
            return max(int(spacing.get("val", "0")), 0) / 100.0
        except ValueError:
            return 0.0
    spacing = spacing_container.find("a:spcPct", NS)
    if spacing is not None:
        try:
            return font_pt * max(int(spacing.get("val", "0")), 0) / 100000.0
        except ValueError:
            return 0.0
    return 0.0


def _paragraph_alignment(
    paragraph: ET.Element,
    body_levels: Mapping[int, ET.Element],
) -> str:
    properties = paragraph.find("a:pPr", NS)
    if properties is not None and properties.get("algn") is not None:
        return properties.get("algn", "l")
    level_properties = body_levels.get(_paragraph_level(paragraph))
    return (
        level_properties.get("algn", "l")
        if level_properties is not None
        else "l"
    )


def _percentage_ratio(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        if value.endswith("%"):
            ratio = float(value[:-1]) / 100.0
        else:
            ratio = int(value) / 100000.0
    except ValueError:
        return default
    return min(max(ratio, 0.0), 1.0)


def _autofit_settings(body_properties: ET.Element) -> tuple[str, float, float]:
    if body_properties.find("a:spAutoFit", NS) is not None:
        return "shape", 1.0, 0.0
    normal = body_properties.find("a:normAutofit", NS)
    if normal is not None:
        return (
            "normal",
            _percentage_ratio(normal.get("fontScale"), 1.0),
            _percentage_ratio(normal.get("lnSpcReduction"), 0.0),
        )
    return "none", 1.0, 0.0


def _xml_shape_details(
    shape: ET.Element,
    box: tuple[int, int, int, int] | None,
) -> dict[str, Any]:
    shape_id, name = _shape_identity(shape)
    details: dict[str, Any] = {"id": shape_id, "name": name}
    if box is None:
        details.update({"bounds_emu": None, "bounds_inches": None})
        return details
    x, y, width, height = box
    details.update(
        {
            "bounds_emu": {"x": x, "y": y, "width": width, "height": height},
            "bounds_inches": {
                "x": round(x / EMU_PER_INCH, 4),
                "y": round(y / EMU_PER_INCH, 4),
                "width": round(width / EMU_PER_INCH, 4),
                "height": round(height / EMU_PER_INCH, 4),
            },
        }
    )
    return details


def _has_rotation(value: str | None) -> bool:
    if value is None:
        return False
    try:
        return int(value) != 0
    except ValueError:
        return True


def _inventory_text_shapes(
    root: ET.Element,
    slide_part: str,
    slide_number: int,
    issues: list[dict[str, Any]],
) -> list[TextShape]:
    """Inventory text frames supported by the V2.3 slide-local estimator."""

    inventory: list[TextShape] = []
    for shape in _top_level_shapes(root):
        if _shape_is_hidden(shape):
            continue
        local_name = _local_name(shape)
        if local_name in {"grpSp", "graphicFrame"} and shape.find(".//a:t", NS) is not None:
            box = _bounds(_shape_transform(shape))
            reason, description = {
                "grpSp": ("grouped_text", "Grouped text"),
                "graphicFrame": ("graphic_frame_text", "Graphic-frame text"),
            }[local_name]
            _add_issue(
                issues,
                "warning",
                "TEXT_LAYOUT_UNSUPPORTED",
                f"{description} is outside the V2.3 text-capacity estimator.",
                part=slide_part,
                slide=slide_number,
                shape=_xml_shape_details(shape, box),
                evidence={"reason": reason},
            )
            continue
        if local_name != "sp":
            continue
        text_body = shape.find("p:txBody", NS)
        if text_body is None:
            continue
        transform = shape.find("p:spPr/a:xfrm", NS)
        box = _bounds(transform)
        if box is None:
            is_placeholder = shape.find("p:nvSpPr/p:nvPr/p:ph", NS) is not None
            has_visible_text = any(
                (node.text or "").strip() for node in text_body.findall(".//a:t", NS)
            )
            if is_placeholder or has_visible_text:
                reason = (
                    "placeholder_without_local_geometry"
                    if is_placeholder
                    else "text_without_local_geometry"
                )
                description = "Placeholder text" if is_placeholder else "Text shape"
                _add_issue(
                    issues,
                    "warning",
                    "TEXT_LAYOUT_UNSUPPORTED",
                    f"{description} has no slide-local geometry for capacity estimation.",
                    part=slide_part,
                    slide=slide_number,
                    shape=_xml_shape_details(shape, None),
                    evidence={"reason": reason},
                )
            continue
        transform_rotation = transform.get("rot") if transform is not None else None
        if _has_rotation(transform_rotation):
            _add_issue(
                issues,
                "warning",
                "TEXT_LAYOUT_UNSUPPORTED",
                "Rotated shape layout is outside the V2.3 text-capacity estimator.",
                part=slide_part,
                slide=slide_number,
                shape=_xml_shape_details(shape, box),
                evidence={"reason": "shape_rotation", "rotation": transform_rotation},
            )
            continue

        body_properties = text_body.find("a:bodyPr", NS)
        if body_properties is None:
            body_properties = ET.Element(f"{{{NS['a']}}}bodyPr")
        body_rotation = body_properties.get("rot")
        if _has_rotation(body_rotation):
            _add_issue(
                issues,
                "warning",
                "TEXT_LAYOUT_UNSUPPORTED",
                "Rotated text-body layout is outside the V2.3 text-capacity estimator.",
                part=slide_part,
                slide=slide_number,
                shape=_xml_shape_details(shape, box),
                evidence={"reason": "body_rotation", "rotation": body_rotation},
            )
            continue
        vertical_mode = body_properties.get("vert")
        if vertical_mode not in {None, "horz"}:
            _add_issue(
                issues,
                "warning",
                "TEXT_LAYOUT_UNSUPPORTED",
                "Vertical text layout is outside the V2.3 text-capacity estimator.",
                part=slide_part,
                slide=slide_number,
                shape=_xml_shape_details(shape, box),
                evidence={"reason": "vertical_text", "vertical_mode": vertical_mode},
            )
            continue
        margins = (
            _integer_attribute(
                body_properties,
                "lIns",
                _DEFAULT_LEFT_RIGHT_MARGIN_EMU,
            ),
            _integer_attribute(
                body_properties,
                "tIns",
                _DEFAULT_TOP_BOTTOM_MARGIN_EMU,
            ),
            _integer_attribute(
                body_properties,
                "rIns",
                _DEFAULT_LEFT_RIGHT_MARGIN_EMU,
            ),
            _integer_attribute(
                body_properties,
                "bIns",
                _DEFAULT_TOP_BOTTOM_MARGIN_EMU,
            ),
        )
        autofit, font_scale, line_spacing_reduction = _autofit_settings(body_properties)
        body_levels = _body_level_properties(text_body)
        paragraphs: list[TextParagraph] = []
        for paragraph in text_body.findall("a:p", NS):
            paragraphs.append(
                _paragraph_metrics(
                    paragraph,
                    body_levels,
                    font_scale,
                )
            )
        if not paragraphs:
            empty_font_pt = DEFAULT_FONT_PT * font_scale
            empty_line = TextLine(
                text="",
                runs=(),
                font_pt=empty_font_pt,
                font_fallback=True,
            )
            paragraphs.append(
                TextParagraph(
                    lines=("",),
                    line_metrics=(empty_line,),
                    spacing_before_pt=0.0,
                    spacing_after_pt=0.0,
                    font_pt=empty_font_pt,
                    font_fallback=True,
                    alignment="l",
                )
            )

        shape_id, name = _shape_identity(shape)
        text = "\n".join(line for paragraph in paragraphs for line in paragraph.lines)
        inventory.append(
            TextShape(
                part=slide_part,
                slide=slide_number,
                shape_id=shape_id,
                name=name,
                bounds_emu=box,
                margins_emu=margins,
                text=text,
                paragraphs=tuple(paragraphs),
                font_pt=max(paragraph.font_pt for paragraph in paragraphs),
                font_fallback=any(paragraph.font_fallback for paragraph in paragraphs),
                autofit=autofit,
                font_scale=font_scale,
                line_spacing_reduction=line_spacing_reduction,
                wrap=body_properties.get("wrap") or "square",
                vertical_anchor=body_properties.get("anchor") or "t",
                is_placeholder=shape.find("p:nvSpPr/p:nvPr/p:ph", NS) is not None,
            )
        )
    return inventory


def _character_width_inches(character: str, font_pt: float) -> float:
    if character.isspace():
        em_width = WHITESPACE_GLYPH_EM
    elif unicodedata.category(character).startswith("P"):
        em_width = PUNCTUATION_GLYPH_EM
    elif unicodedata.east_asian_width(character) in {"W", "F"}:
        em_width = CJK_GLYPH_EM
    elif unicodedata.category(character).startswith("M"):
        em_width = 0.0
    else:
        em_width = LATIN_GLYPH_EM
    return em_width * font_pt / 72.0


def _text_width_inches(text: str, font_pt: float) -> float:
    return sum(_character_width_inches(character, font_pt) for character in text)


def _split_long_word(
    word: str,
    font_pt: float,
    available_width_in: float,
) -> list[float]:
    widths: list[float] = []
    current = 0.0
    for character in word:
        character_width = _character_width_inches(character, font_pt)
        if current and current + character_width > available_width_in:
            widths.append(current)
            current = 0.0
        current += character_width
    widths.append(current)
    return widths


def _wrapped_line_widths(
    text: str,
    font_pt: float,
    available_width_in: float,
    wrap: str,
) -> list[float]:
    width = _text_width_inches(text, font_pt)
    if wrap == "none" or not text:
        return [width]
    if available_width_in <= 0:
        return [_character_width_inches(character, font_pt) for character in text] or [0.0]

    line_widths: list[float] = []
    current_width = 0.0
    pending_space_width = 0.0
    for token in re.findall(r"\s+|[^\s]+", text):
        token_width = _text_width_inches(token, font_pt)
        if token.isspace():
            if current_width:
                pending_space_width += token_width
            continue

        candidate_width = current_width + pending_space_width + token_width
        if current_width and candidate_width <= available_width_in:
            current_width = candidate_width
            pending_space_width = 0.0
            continue
        if current_width:
            line_widths.append(current_width)
            current_width = 0.0
            pending_space_width = 0.0
        if token_width <= available_width_in:
            current_width = token_width
            continue

        split_widths = _split_long_word(token, font_pt, available_width_in)
        line_widths.extend(split_widths[:-1])
        current_width = split_widths[-1]

    line_widths.append(current_width)
    return line_widths


def _styled_metrics(
    characters: list[tuple[str, float]],
    default_font_pt: float,
) -> tuple[float, float]:
    if not characters:
        return 0.0, default_font_pt
    return (
        sum(_character_width_inches(character, font_pt) for character, font_pt in characters),
        max(font_pt for _, font_pt in characters),
    )


def _wrapped_text_line_metrics(
    line: TextLine,
    available_width_in: float,
    wrap: str,
) -> list[tuple[float, float]]:
    characters = [
        (character, run.font_pt)
        for run in line.runs
        for character in run.text
    ]
    if wrap == "none" or not characters:
        return [_styled_metrics(characters, line.font_pt)]
    if available_width_in <= 0:
        return [
            (_character_width_inches(character, font_pt), font_pt)
            for character, font_pt in characters
        ]

    tokens: list[tuple[bool, list[tuple[str, float]]]] = []
    for character in characters:
        is_whitespace = character[0].isspace()
        if tokens and tokens[-1][0] == is_whitespace:
            tokens[-1][1].append(character)
        else:
            tokens.append((is_whitespace, [character]))

    wrapped: list[tuple[float, float]] = []
    current: list[tuple[str, float]] = []
    pending_spaces: list[tuple[str, float]] = []
    for is_whitespace, token in tokens:
        if is_whitespace:
            if current:
                pending_spaces.extend(token)
            continue

        candidate = current + pending_spaces + token
        candidate_width, _ = _styled_metrics(candidate, line.font_pt)
        if current and candidate_width <= available_width_in:
            current = candidate
            pending_spaces = []
            continue
        if current:
            wrapped.append(_styled_metrics(current, line.font_pt))
            current = []
            pending_spaces = []

        token_width, _ = _styled_metrics(token, line.font_pt)
        if token_width <= available_width_in:
            current = token
            continue

        partial: list[tuple[str, float]] = []
        for character in token:
            candidate_width, _ = _styled_metrics(partial + [character], line.font_pt)
            if partial and candidate_width > available_width_in:
                wrapped.append(_styled_metrics(partial, line.font_pt))
                partial = []
            partial.append(character)
        current = partial

    if current:
        wrapped.append(_styled_metrics(current, line.font_pt))
    return wrapped or [(0.0, line.font_pt)]


def _shape_details(shape: TextShape) -> dict[str, Any]:
    x, y, width, height = shape.bounds_emu
    return {
        "id": shape.shape_id,
        "name": shape.name,
        "bounds_emu": {"x": x, "y": y, "width": width, "height": height},
        "bounds_inches": {
            "x": round(x / EMU_PER_INCH, 4),
            "y": round(y / EMU_PER_INCH, 4),
            "width": round(width / EMU_PER_INCH, 4),
            "height": round(height / EMU_PER_INCH, 4),
        },
    }


def _estimate_text_capacity(
    shape: TextShape,
    available_width_in: float | None = None,
) -> dict[str, Any]:
    _, _, width, height = shape.bounds_emu
    left, top, right, bottom = shape.margins_emu
    declared_width_in = max(width - left - right, 0) / EMU_PER_INCH
    if available_width_in is None:
        available_width_in = declared_width_in
    else:
        available_width_in = max(available_width_in, 0.0)
    available_height_in = max(height - top - bottom, 0) / EMU_PER_INCH

    estimated_lines = 0
    max_line_width_in = 0.0
    required_height_in = 0.0
    if shape.text.strip():
        for paragraph in shape.paragraphs:
            paragraph_lines = 0
            for line in paragraph.line_metrics:
                line_metrics = _wrapped_text_line_metrics(
                    line,
                    available_width_in,
                    shape.wrap,
                )
                paragraph_lines += len(line_metrics)
                max_line_width_in = max(
                    max_line_width_in,
                    *(width for width, _ in line_metrics),
                )
                required_height_in += sum(
                    font_pt
                    * max(LINE_HEIGHT_FACTOR - shape.line_spacing_reduction, 0.0)
                    / 72.0
                    for _, font_pt in line_metrics
                )
            estimated_lines += paragraph_lines
            required_height_in += (
                paragraph.spacing_before_pt + paragraph.spacing_after_pt
            ) / 72.0

    denominator = max(available_height_in, 1e-9)
    return {
        "estimated_lines": estimated_lines,
        "font_pt": shape.font_pt,
        "max_line_width_in": max_line_width_in,
        "available_width_in": available_width_in,
        "required_height_in": required_height_in,
        "available_height_in": available_height_in,
        "utilization": required_height_in / denominator,
        "autofit": shape.autofit,
        "font_scale": shape.font_scale,
        "line_spacing_reduction": shape.line_spacing_reduction,
        "wrap": shape.wrap,
        "font_fallback": shape.font_fallback,
    }


def _occupied_text_rect(shape: TextShape) -> tuple[float, float, float, float]:
    """Estimate the text block rectangle inside a supported text frame."""

    x, y, width, height = shape.bounds_emu
    left_margin, top_margin, right_margin, bottom_margin = shape.margins_emu
    usable_left = (x + left_margin) / EMU_PER_INCH
    usable_top = (y + top_margin) / EMU_PER_INCH
    usable_width = max(width - left_margin - right_margin, 0) / EMU_PER_INCH
    usable_height = max(height - top_margin - bottom_margin, 0) / EMU_PER_INCH

    if not shape.text.strip():
        return usable_left, usable_top, usable_left, usable_top

    horizontal_intervals: list[tuple[float, float]] = []
    for paragraph in shape.paragraphs:
        for line in paragraph.line_metrics:
            for line_width, _ in _wrapped_text_line_metrics(
                line,
                usable_width,
                shape.wrap,
            ):
                occupied_width = min(line_width, usable_width)
                if paragraph.alignment == "ctr":
                    line_left = usable_left + (usable_width - occupied_width) / 2
                elif paragraph.alignment == "r":
                    line_left = usable_left + usable_width - occupied_width
                else:
                    line_left = usable_left
                    if paragraph.alignment in {"dist", "just", "thaiDist"}:
                        occupied_width = usable_width
                horizontal_intervals.append((line_left, line_left + occupied_width))

    if horizontal_intervals:
        occupied_left = min(interval[0] for interval in horizontal_intervals)
        occupied_right = max(interval[1] for interval in horizontal_intervals)
    else:
        occupied_left = occupied_right = usable_left

    required_height = _estimate_text_capacity(shape)["required_height_in"]
    if shape.autofit == "shape":
        occupied_height = required_height
    else:
        occupied_height = min(required_height, usable_height)
    if shape.vertical_anchor == "ctr":
        occupied_top = usable_top + (usable_height - occupied_height) / 2
    elif shape.vertical_anchor == "b":
        occupied_top = usable_top + usable_height - occupied_height
    else:
        occupied_top = usable_top
    return (
        occupied_left,
        occupied_top,
        occupied_right,
        occupied_top + occupied_height,
    )


def _rect_intersection_inches(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> tuple[float, float] | None:
    width = min(first[2], second[2]) - max(first[0], second[0])
    height = min(first[3], second[3]) - max(first[1], second[1])
    return (width, height) if width > 0 and height > 0 else None


def _rects_approach(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
    distance: float,
) -> bool:
    horizontal_overlap = min(first[2], second[2]) - max(first[0], second[0])
    vertical_overlap = min(first[3], second[3]) - max(first[1], second[1])
    horizontal_gap = max(second[0] - first[2], first[0] - second[2], 0.0)
    vertical_gap = max(second[1] - first[3], first[1] - second[3], 0.0)
    return (
        horizontal_overlap > 0 and vertical_gap <= distance
    ) or (
        vertical_overlap > 0 and horizontal_gap <= distance
    )


def _is_clear_text_overflow(estimate: Mapping[str, Any]) -> bool:
    required_height = float(estimate["required_height_in"])
    available_height = float(estimate["available_height_in"])
    return (
        required_height - available_height > OVERFLOW_TOLERANCE_IN
        and required_height > available_height * OVERFLOW_RATIO
    )


def _enters_footer_zone(
    bounds_emu: tuple[int, int, int, int],
    slide_height: int,
) -> bool:
    if slide_height <= 0:
        return False
    _, y, _, height = bounds_emu
    footer_top = slide_height * (1.0 - FOOTER_ZONE_RATIO)
    return y + height > footer_top


def _page_number_markers(
    shapes: list[TextShape],
    slide_width: int,
    slide_height: int,
) -> list[PageNumberMarker]:
    if slide_width <= 0 or slide_height <= 0:
        return []
    slide_width_in = slide_width / EMU_PER_INCH
    slide_center = slide_width / 2.0
    markers: list[PageNumberMarker] = []
    for shape in shapes:
        if not _enters_footer_zone(shape.bounds_emu, slide_height):
            continue
        if PAGE_NUMBER_RE.fullmatch(shape.text) is None:
            continue
        x, y, width, height = shape.bounds_emu
        if x >= slide_width * PAGE_NUMBER_FAR_RIGHT_RATIO:
            position = "right"
            safe_left = x / EMU_PER_INCH - PAGE_NUMBER_CLEARANCE_IN
            safe_right = slide_width_in
        elif x <= slide_center <= x + width:
            position = "center"
            safe_left = x / EMU_PER_INCH - PAGE_NUMBER_CLEARANCE_IN
            safe_right = (x + width) / EMU_PER_INCH + PAGE_NUMBER_CLEARANCE_IN
        else:
            continue
        markers.append(
            PageNumberMarker(
                shape=shape,
                position=position,
                safe_left_in=max(safe_left, 0.0),
                safe_top_in=y / EMU_PER_INCH,
                safe_right_in=min(safe_right, slide_width_in),
                safe_bottom_in=(y + height) / EMU_PER_INCH,
            )
        )
    return markers


def _safe_footer_width(shape: TextShape, marker: PageNumberMarker) -> float:
    x, _, width, _ = shape.bounds_emu
    left_margin, _, right_margin, _ = shape.margins_emu
    usable_left = (x + left_margin) / EMU_PER_INCH
    usable_right = (x + width - right_margin) / EMU_PER_INCH
    if marker.position == "right":
        return max(min(usable_right, marker.safe_left_in) - usable_left, 0.0)

    marker_center = (marker.safe_left_in + marker.safe_right_in) / 2.0
    frame_center = (usable_left + usable_right) / 2.0
    if frame_center <= marker_center:
        return max(min(usable_right, marker.safe_left_in) - usable_left, 0.0)
    return max(usable_right - max(usable_left, marker.safe_right_in), 0.0)


def _page_marker_evidence(marker: PageNumberMarker) -> dict[str, Any]:
    return {
        "id": marker.shape.shape_id,
        "name": marker.shape.name,
        "position": marker.position,
        "safe_zone_inches": {
            "left": round(marker.safe_left_in, 4),
            "top": round(marker.safe_top_in, 4),
            "right": round(marker.safe_right_in, 4),
            "bottom": round(marker.safe_bottom_in, 4),
        },
    }


def _check_footer_safe_zone(
    shapes: list[TextShape],
    slide_width: int,
    slide_height: int,
    issues: list[dict[str, Any]],
) -> None:
    markers = _page_number_markers(shapes, slide_width, slide_height)
    marker_shapes = {id(marker.shape) for marker in markers}
    footer_shapes = [
        shape
        for shape in shapes
        if shape.text.strip()
        and id(shape) not in marker_shapes
        and _enters_footer_zone(shape.bounds_emu, slide_height)
    ]
    for shape in footer_shapes:
        declared_estimate = _estimate_text_capacity(shape)
        overflow_estimate = declared_estimate
        for marker in markers:
            safe_width = _safe_footer_width(shape, marker)
            safe_estimate = _estimate_text_capacity(shape, safe_width)
            occupied_left, occupied_top, occupied_right, occupied_bottom = (
                _occupied_text_rect(shape)
            )
            horizontal_intrusion = min(occupied_right, marker.safe_right_in) - max(
                occupied_left,
                marker.safe_left_in,
            )
            vertical_intrusion = min(occupied_bottom, marker.safe_bottom_in) - max(
                occupied_top,
                marker.safe_top_in,
            )
            if (
                vertical_intrusion >= COLLISION_TOLERANCE_IN
                and safe_estimate["required_height_in"]
                > overflow_estimate["required_height_in"]
            ):
                overflow_estimate = safe_estimate
            line_count_increase = (
                safe_estimate["estimated_lines"] - declared_estimate["estimated_lines"]
            )
            if (
                vertical_intrusion < COLLISION_TOLERANCE_IN
                or (
                    horizontal_intrusion <= 0
                    or (
                        line_count_increase < 1
                        and horizontal_intrusion < COLLISION_TOLERANCE_IN
                    )
                )
            ):
                continue
            _add_issue(
                issues,
                "error",
                "FOOTER_PAGE_NUMBER_COLLISION",
                f'Footer text "{shape.name}" enters the reserved page-number zone.',
                part=shape.part,
                slide=shape.slide,
                shape=_shape_details(shape),
                evidence={
                    "page_number": _page_marker_evidence(marker),
                    "declared_width_lines": declared_estimate["estimated_lines"],
                    "safe_width_lines": safe_estimate["estimated_lines"],
                    "line_count_increase": line_count_increase,
                    "safe_available_width_in": round(safe_width, 4),
                    "reserved_zone_intrusion_in": round(
                        max(horizontal_intrusion, 0.0),
                        4,
                    ),
                    "reserved_zone_vertical_intrusion_in": round(
                        max(vertical_intrusion, 0.0),
                        4,
                    ),
                    "collision_tolerance_in": COLLISION_TOLERANCE_IN,
                },
            )

        if shape.autofit != "shape" and _is_clear_text_overflow(overflow_estimate):
            _add_issue(
                issues,
                "error",
                "FOOTER_TEXT_OVERFLOW",
                "Estimated footer text height exceeds the usable footer-frame height.",
                part=shape.part,
                slide=shape.slide,
                shape=_shape_details(shape),
                evidence=overflow_estimate,
            )


def _check_table_footer_collisions(
    root: ET.Element,
    slide_part: str,
    slide_number: int,
    slide_height: int,
    issues: list[dict[str, Any]],
) -> None:
    if slide_height <= 0:
        return
    footer_top = slide_height * (1.0 - FOOTER_ZONE_RATIO)
    tolerance_emu = COLLISION_TOLERANCE_IN * EMU_PER_INCH
    for shape in _top_level_shapes(root):
        if _local_name(shape) != "graphicFrame" or _shape_is_hidden(shape):
            continue
        if shape.find("a:graphic/a:graphicData/a:tbl", NS) is None:
            continue
        box = _bounds(_shape_transform(shape))
        if box is None:
            continue
        _, y, _, height = box
        footer_overlap = y + height - footer_top
        if footer_overlap < tolerance_emu:
            continue
        _add_issue(
            issues,
            "error",
            "TABLE_FOOTER_COLLISION",
            "Top-level table materially enters the footer/source safe band.",
            part=slide_part,
            slide=slide_number,
            shape=_xml_shape_details(shape, box),
            evidence={
                "footer_zone_ratio": FOOTER_ZONE_RATIO,
                "footer_zone_top_in": round(footer_top / EMU_PER_INCH, 4),
                "footer_overlap_in": round(footer_overlap / EMU_PER_INCH, 4),
                "collision_tolerance_in": COLLISION_TOLERANCE_IN,
            },
        )


def _check_text_collisions(
    shapes: list[TextShape],
    issues: list[dict[str, Any]],
) -> None:
    visible_shapes = [shape for shape in shapes if shape.text.strip()]
    tolerance_emu = COLLISION_TOLERANCE_IN * EMU_PER_INCH
    reported_pairs: set[frozenset[int]] = set()
    for index, first in enumerate(visible_shapes):
        first_x, first_y, first_width, first_height = first.bounds_emu
        for second in visible_shapes[index + 1 :]:
            second_x, second_y, second_width, second_height = second.bounds_emu
            exact_duplicate_bounds = first.bounds_emu == second.bounds_emu
            intersection_width_emu = min(
                first_x + first_width,
                second_x + second_width,
            ) - max(first_x, second_x)
            intersection_height_emu = min(
                first_y + first_height,
                second_y + second_height,
            ) - max(first_y, second_y)
            if not exact_duplicate_bounds and (
                intersection_width_emu < tolerance_emu
                or intersection_height_emu < tolerance_emu
            ):
                continue

            occupied_intersection = _rect_intersection_inches(
                _occupied_text_rect(first),
                _occupied_text_rect(second),
            )
            if not exact_duplicate_bounds and occupied_intersection is None:
                continue

            evidence: dict[str, Any] = {
                "shapes": [
                    {"id": first.shape_id, "name": first.name},
                    {"id": second.shape_id, "name": second.name},
                ],
                "intersection_inches": {
                    "width": round(intersection_width_emu / EMU_PER_INCH, 4),
                    "height": round(intersection_height_emu / EMU_PER_INCH, 4),
                },
                "exact_duplicate_bounds": exact_duplicate_bounds,
            }
            if occupied_intersection is not None:
                evidence["occupied_intersection_inches"] = {
                    "width": round(occupied_intersection[0], 4),
                    "height": round(occupied_intersection[1], 4),
                }
            _add_issue(
                issues,
                "error",
                "TEXT_BOX_COLLISION",
                f'Text frames "{first.name}" and "{second.name}" materially overlap.',
                part=first.part,
                slide=first.slide,
                shape=_shape_details(first),
                evidence=evidence,
            )
            reported_pairs.add(frozenset((id(first), id(second))))

    for growing in visible_shapes:
        explicit_lines = sum(
            len(paragraph.line_metrics)
            for paragraph in growing.paragraphs
        )
        if growing.autofit != "shape" or explicit_lines <= 1:
            continue
        if not _is_clear_text_overflow(_estimate_text_capacity(growing)):
            continue
        growing_rect = _occupied_text_rect(growing)
        for neighbor in visible_shapes:
            pair = frozenset((id(growing), id(neighbor)))
            if neighbor is growing or pair in reported_pairs:
                continue
            intersection = _rect_intersection_inches(
                growing_rect,
                _occupied_text_rect(neighbor),
            )
            if intersection is None or (
                intersection[0] < COLLISION_TOLERANCE_IN
                or intersection[1] < COLLISION_TOLERANCE_IN
            ):
                continue
            _add_issue(
                issues,
                "error",
                "TEXT_BOX_COLLISION",
                f'Expanded shape-to-fit text "{growing.name}" collides with "{neighbor.name}".',
                part=growing.part,
                slide=growing.slide,
                shape=_shape_details(growing),
                evidence={
                    "shapes": [
                        {"id": growing.shape_id, "name": growing.name},
                        {"id": neighbor.shape_id, "name": neighbor.name},
                    ],
                    "occupied_intersection_inches": {
                        "width": round(intersection[0], 4),
                        "height": round(intersection[1], 4),
                    },
                    "autofit_expansion": True,
                    "explicit_lines": explicit_lines,
                },
            )
            reported_pairs.add(pair)


def _check_autofit_growth(
    shapes: list[TextShape],
    slide_height: int,
    issues: list[dict[str, Any]],
) -> None:
    visible_shapes = [shape for shape in shapes if shape.text.strip()]
    slide_height_in = slide_height / EMU_PER_INCH if slide_height else 0.0
    for shape in visible_shapes:
        if shape.autofit != "shape":
            continue
        if PAGE_NUMBER_RE.fullmatch(shape.text) is not None:
            continue
        estimate = _estimate_text_capacity(shape)
        if estimate["required_height_in"] <= estimate["available_height_in"]:
            continue

        expanded_occupancy = _occupied_text_rect(shape)
        risks: list[dict[str, Any]] = []
        for neighbor in visible_shapes:
            if neighbor is shape:
                continue
            neighbor_x, neighbor_y, neighbor_width, neighbor_height = neighbor.bounds_emu
            neighbor_frame = (
                neighbor_x / EMU_PER_INCH,
                neighbor_y / EMU_PER_INCH,
                (neighbor_x + neighbor_width) / EMU_PER_INCH,
                (neighbor_y + neighbor_height) / EMU_PER_INCH,
            )
            if _rects_approach(
                expanded_occupancy,
                neighbor_frame,
                AUTOFIT_APPROACH_IN,
            ):
                risks.append(
                    {
                        "type": "text_shape",
                        "id": neighbor.shape_id,
                        "name": neighbor.name,
                    }
                )

        if slide_height_in and (
            expanded_occupancy[1] <= AUTOFIT_APPROACH_IN
            or slide_height_in - expanded_occupancy[3] <= AUTOFIT_APPROACH_IN
        ):
            risks.append({"type": "slide_edge", "axis": "vertical"})
        footer_zone_top = slide_height_in * (1.0 - FOOTER_ZONE_RATIO)
        if slide_height_in and expanded_occupancy[3] >= (
            footer_zone_top - AUTOFIT_APPROACH_IN
        ):
            risks.append({"type": "footer_safe_zone"})
        if not risks:
            continue

        _add_issue(
            issues,
            "warning",
            "AUTOFIT_GROWTH_RISK",
            "Shape-to-fit-text growth approaches another text frame, the slide edge, or the footer safe zone.",
            part=shape.part,
            slide=shape.slide,
            shape=_shape_details(shape),
            evidence={
                **estimate,
                "approach_threshold_in": AUTOFIT_APPROACH_IN,
                "risks": risks,
            },
        )


def _check_text_capacity(shape: TextShape, issues: list[dict[str, Any]]) -> None:
    if not shape.text.strip():
        return
    evidence = _estimate_text_capacity(shape)
    shape_details = _shape_details(shape)
    utilization = evidence["utilization"]

    if shape.font_fallback:
        _add_issue(
            issues,
            "warning",
            "TEXT_METRICS_FALLBACK",
            f"One or more text runs use the {DEFAULT_FONT_PT:.0f} pt fallback because no slide-local size is declared.",
            part=shape.part,
            slide=shape.slide,
            shape=shape_details,
            evidence=evidence,
        )

    explicit_lines = sum(
        len(paragraph.line_metrics)
        for paragraph in shape.paragraphs
    )
    if _is_clear_text_overflow(evidence) and (
        shape.autofit != "shape" or explicit_lines > 1
    ):
        _add_issue(
            issues,
            "error",
            "TEXT_FRAME_OVERFLOW",
            "Estimated text height exceeds the usable text-frame height.",
            part=shape.part,
            slide=shape.slide,
            shape=shape_details,
            evidence=evidence,
        )
    elif utilization >= NEAR_CAPACITY_RATIO and shape.autofit != "shape":
        _add_issue(
            issues,
            "warning",
            "NEAR_TEXT_CAPACITY",
            "Estimated text height is near the usable text-frame capacity.",
            part=shape.part,
            slide=shape.slide,
            shape=shape_details,
            evidence=evidence,
        )


def _extract_text(root: ET.Element) -> str:
    return " ".join((node.text or "").strip() for node in root.findall(".//a:t", NS)).strip()


def _font_sizes(root: ET.Element) -> list[int]:
    sizes: list[int] = []
    for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
        for node in root.findall(f".//{tag}", NS):
            value = node.get("sz")
            if value and value.isdigit():
                sizes.append(int(value))
    return sizes


def _font_faces(root: ET.Element) -> set[str]:
    faces: set[str] = set()
    for tag in ("a:latin", "a:ea", "a:cs"):
        for node in root.findall(f".//{tag}", NS):
            face = node.get("typeface")
            if face and not face.startswith("+"):
                faces.add(face)
    return faces


def _minimum_font_pt(shape: TextShape) -> float:
    values = [
        run.font_pt
        for paragraph in shape.paragraphs
        for line in paragraph.line_metrics
        for run in line.runs
        if run.text.strip()
    ]
    return min(values) if values else shape.font_pt


def _text_role(shape: TextShape, slide_height: int) -> str:
    """Classify only stable top-level roles; ambiguous text remains body text."""

    text = shape.text.strip()
    _, y, _, height = shape.bounds_emu
    if PAGE_NUMBER_RE.fullmatch(text):
        return "page_number"
    if slide_height and y + height >= slide_height * (1.0 - FOOTER_ZONE_RATIO):
        return "source_or_footer"
    lowered = text.lower()
    if any(lowered.startswith(marker) for marker in SOURCE_MARKERS):
        return "source_or_footer"
    if slide_height and y <= slide_height * 0.20 and height <= slide_height * 0.22 and shape.font_pt >= 18:
        return "title"
    return "body"


def _check_body_text(
    shapes: list[TextShape],
    slide_height: int,
    issues: list[dict[str, Any]],
) -> None:
    undersized: list[tuple[TextShape, float]] = []
    fragile_autofit: list[tuple[TextShape, float, dict[str, Any]]] = []
    for shape in shapes:
        if not shape.text.strip() or _text_role(shape, slide_height) != "body":
            continue
        minimum = _minimum_font_pt(shape)
        if minimum < MIN_BODY_FONT_PT:
            undersized.append((shape, minimum))
        if shape.autofit == "shape":
            estimate = _estimate_text_capacity(shape)
            if estimate["utilization"] >= NEAR_CAPACITY_RATIO or minimum < AUTOFIT_REVIEW_FONT_PT:
                fragile_autofit.append((shape, minimum, estimate))

    if undersized:
        first, _ = undersized[0]
        _add_issue(
            issues,
            "warning",
            "BODY_FONT_TOO_SMALL",
            f"Slide contains {len(undersized)} body text frame(s) below the 10 pt delivery threshold.",
            part=first.part,
            slide=first.slide,
            shape=_shape_details(first),
            evidence={
                "count": len(undersized),
                "minimum_font_pt": round(min(value for _, value in undersized), 2),
                "examples": [
                    {"id": shape.shape_id, "name": shape.name, "font_pt": round(value, 2)}
                    for shape, value in undersized[:8]
                ],
            },
        )
    if fragile_autofit:
        first, _, _ = fragile_autofit[0]
        _add_issue(
            issues,
            "warning",
            "SHAPE_TO_FIT_BODY_TEXT",
            f"Slide contains {len(fragile_autofit)} body frame(s) with fragile shape-to-fit-text behavior.",
            part=first.part,
            slide=first.slide,
            shape=_shape_details(first),
            evidence={
                "count": len(fragile_autofit),
                "minimum_font_pt": round(min(value for _, value, _ in fragile_autofit), 2),
                "maximum_utilization": round(max(item["utilization"] for _, _, item in fragile_autofit), 4),
                "review_utilization_threshold": NEAR_CAPACITY_RATIO,
                "review_font_threshold_pt": AUTOFIT_REVIEW_FONT_PT,
                "examples": [
                    {
                        "id": shape.shape_id,
                        "name": shape.name,
                        "font_pt": round(value, 2),
                        "utilization": round(estimate["utilization"], 4),
                    }
                    for shape, value, estimate in fragile_autofit[:8]
                ],
            },
        )


def _normalized_box(shape: TextShape, slide_width: int, slide_height: int) -> tuple[float, float, float, float]:
    x, y, width, height = shape.bounds_emu
    slide_width = max(slide_width, 1)
    slide_height = max(slide_height, 1)
    return (
        round(x / slide_width, 2),
        round(y / slide_height, 2),
        round(width / slide_width, 2),
        round(height / slide_height, 2),
    )


def _consistency_record(
    shapes: list[TextShape],
    fonts: set[str],
    slide_number: int,
    slide_width: int,
    slide_height: int,
) -> dict[str, Any]:
    visible = [shape for shape in shapes if shape.text.strip()]
    titles = [shape for shape in visible if _text_role(shape, slide_height) == "title"]
    title = max(titles, key=lambda item: (item.font_pt, -item.bounds_emu[1]), default=None)
    body_sizes = sorted({round(_minimum_font_pt(shape), 1) for shape in visible if _text_role(shape, slide_height) == "body"})
    furniture = sorted(
        _normalized_box(shape, slide_width, slide_height)
        for shape in visible
        if _text_role(shape, slide_height) in {"source_or_footer", "page_number"}
    )
    return {
        "slide": slide_number,
        "title_geometry": _normalized_box(title, slide_width, slide_height) if title is not None else None,
        "page_furniture": tuple(furniture),
        "type_scale": tuple(body_sizes),
        "fonts": tuple(sorted(fonts)),
    }


def _check_recurring_drift(
    records: list[dict[str, Any]],
    key: str,
    code: str,
    message: str,
    issues: list[dict[str, Any]],
) -> None:
    populated = [(record["slide"], record[key]) for record in records if record.get(key)]
    if len(populated) < 4:
        return
    counts = Counter(value for _, value in populated)
    baseline, count = counts.most_common(1)[0]
    if count < max(3, int(len(populated) * 0.6 + 0.5)):
        return
    for slide, value in populated:
        if value == baseline:
            continue
        _add_issue(
            issues,
            "warning",
            code,
            message,
            slide=slide,
            evidence={"dominant": baseline, "observed": value, "dominant_slides": count},
        )


def _check_cross_slide_consistency(records: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    _check_recurring_drift(records, "title_geometry", "TITLE_GEOMETRY_DRIFT", "Title geometry differs from the recurring deck pattern.", issues)
    _check_recurring_drift(records, "page_furniture", "PAGE_FURNITURE_DRIFT", "Footer or page furniture differs from the recurring deck pattern.", issues)
    _check_recurring_drift(records, "type_scale", "TYPE_SCALE_DRIFT", "Body type scale differs from the recurring deck pattern.", issues)
    _check_recurring_drift(records, "fonts", "FONT_FAMILY_DRIFT", "Font-family usage differs from the recurring deck pattern.", issues)


def _check_slide(
    root: ET.Element,
    slide_part: str,
    slide_number: int,
    slide_width: int,
    slide_height: int,
    issues: list[dict[str, Any]],
) -> tuple[set[str], dict[str, Any]]:
    text = _extract_text(root)
    if PLACEHOLDER_RE.search(text):
        _add_issue(
            issues,
            "warning",
            "PLACEHOLDER_TEXT",
            "Slide contains placeholder or draft text.",
            part=slide_part,
            slide=slide_number,
        )

    sizes = _font_sizes(root)
    if sizes and min(sizes) < MIN_WARN_FONT_SIZE:
        _add_issue(
            issues,
            "warning",
            "SMALL_FONT",
            f"Slide contains text below 9 pt (minimum {min(sizes) / 100:.1f} pt).",
            part=slide_part,
            slide=slide_number,
        )

    shapes = _top_level_shapes(root)
    large_picture = False
    for shape in shapes:
        box = _bounds(_shape_transform(shape))
        if box is None:
            continue
        x, y, width, height = box
        if width < 0 or height < 0 or x < 0 or y < 0 or (
            slide_width and x + width > slide_width
        ) or (slide_height and y + height > slide_height):
            scale = max(slide_width, slide_height, 1)
            extreme_coordinates = max(abs(x), abs(y), abs(width), abs(height)) > scale * 10
            visible_text = "".join(
                node.text or "" for node in shape.findall(".//a:t", NS)
            ).strip()
            _add_issue(
                issues,
                "error",
                "OUT_OF_BOUNDS",
                f"Object bounds ({x}, {y}, {width}, {height}) exceed the slide canvas.",
                part=slide_part,
                slide=slide_number,
                shape=_xml_shape_details(shape, box),
                evidence={
                    "shape_kind": _local_name(shape),
                    "has_visible_text": bool(visible_text),
                    "visible_text_preview": visible_text[:120],
                    "extreme_coordinates": extreme_coordinates,
                    "slide_width_emu": slide_width,
                    "slide_height_emu": slide_height,
                },
            )
        if shape.tag.rsplit("}", 1)[-1] == "pic" and slide_width and slide_height:
            area_ratio = max(width, 0) * max(height, 0) / (slide_width * slide_height)
            large_picture = large_picture or area_ratio >= 0.90

    if large_picture and len(text) < 20:
        _add_issue(
            issues,
            "warning",
            "FLATTENED_SLIDE",
            "A near-full-slide image with little editable text may be an unintentionally flattened slide.",
            part=slide_part,
            slide=slide_number,
        )

    if root.find(".//c:chart", NS) is not None and not any(marker in text.lower() for marker in SOURCE_MARKERS):
        _add_issue(
            issues,
            "warning",
            "CHART_SOURCE_MISSING",
            "Chart slide has no visible source marker.",
            part=slide_part,
            slide=slide_number,
        )

    text_shapes = _inventory_text_shapes(root, slide_part, slide_number, issues)
    for text_shape in text_shapes:
        _check_text_capacity(text_shape, issues)
    _check_body_text(text_shapes, slide_height, issues)
    _check_text_collisions(text_shapes, issues)
    _check_autofit_growth(text_shapes, slide_height, issues)
    _check_footer_safe_zone(
        text_shapes,
        slide_width,
        slide_height,
        issues,
    )
    _check_table_footer_collisions(
        root,
        slide_part,
        slide_number,
        slide_height,
        issues,
    )

    fonts = _font_faces(root)
    return fonts, _consistency_record(
        text_shapes,
        fonts,
        slide_number,
        slide_width,
        slide_height,
    )


def validate_pptx(
    path: str | Path,
    expected_aspect_ratio: str | None = None,
) -> dict[str, Any]:
    pptx_path = Path(path)
    issues: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "version": "2.3",
        "file": str(pptx_path),
        "summary": {
            "slide_count": 0,
            "notes_count": 0,
            "external_relationships": 0,
            "slide_size_emu": {"width": 0, "height": 0},
            "slide_size_inches": {"width": 0.0, "height": 0.0},
            "fonts": [],
            "chart_pages": [],
            "has_embedded_fonts": False,
            "blocking": 0,
            "review_required": 0,
            "advisories": 0,
            "tool_failures": 0,
            "errors": 0,
            "warnings": 0,
        },
        "issues": issues,
    }

    expected_ratio: float | None = None
    if expected_aspect_ratio is not None:
        try:
            expected_ratio = _parse_aspect_ratio(expected_aspect_ratio)
        except ValueError as exc:
            _add_issue(
                issues,
                "error",
                "INVALID_EXPECTED_ASPECT_RATIO",
                f"Invalid expected aspect ratio {expected_aspect_ratio!r}: {exc}.",
            )

    if not pptx_path.is_file():
        _add_issue(issues, "error", "FILE_NOT_FOUND", f"PPTX file not found: {pptx_path}")
        return _finalize_report(report)

    try:
        with zipfile.ZipFile(pptx_path) as package:
            names = set(package.namelist())
            for part in sorted(REQUIRED_PARTS - names):
                _add_issue(issues, "error", "MISSING_PART", f"Required package part is missing: {part}", part=part)

            report["summary"]["external_relationships"] = _check_relationships(package, names, issues)
            slide_width, slide_height = _presentation_size(package, issues)
            report["summary"]["slide_size_emu"] = {"width": slide_width, "height": slide_height}
            report["summary"]["slide_size_inches"] = {
                "width": round(slide_width / EMU_PER_INCH, 3) if slide_width else 0.0,
                "height": round(slide_height / EMU_PER_INCH, 3) if slide_height else 0.0,
            }
            if expected_ratio is not None and slide_width > 0 and slide_height > 0:
                actual_ratio = slide_width / slide_height
                relative_difference = abs(actual_ratio - expected_ratio) / expected_ratio
                if relative_difference > ASPECT_RATIO_TOLERANCE:
                    _add_issue(
                        issues,
                        "error",
                        "ASPECT_RATIO_MISMATCH",
                        "Slide canvas does not match the expected aspect ratio.",
                        evidence={
                            "expected": expected_aspect_ratio,
                            "expected_value": round(expected_ratio, 6),
                            "actual_value": round(actual_ratio, 6),
                            "relative_difference": round(relative_difference, 6),
                            "tolerance": ASPECT_RATIO_TOLERANCE,
                        },
                    )

            slide_parts = sorted(
                (name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=_slide_number,
            )
            report["summary"]["slide_count"] = len(slide_parts)
            report["summary"]["notes_count"] = len(
                [name for name in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)]
            )
            report["summary"]["has_embedded_fonts"] = any(
                name.startswith("ppt/fonts/") for name in names
            )
            if not slide_parts:
                _add_issue(issues, "error", "NO_SLIDES", "The package contains no slide XML parts.")

            fonts: set[str] = set()
            consistency_records: list[dict[str, Any]] = []
            chart_pages: list[int] = []
            for slide_part in slide_parts:
                root = _parse_xml(package, slide_part, issues)
                if root is None:
                    continue
                slide_number = _slide_number(slide_part)
                if root.find(".//c:chart", NS) is not None:
                    chart_pages.append(slide_number)
                slide_fonts, consistency = _check_slide(
                    root,
                    slide_part,
                    slide_number,
                    slide_width,
                    slide_height,
                    issues,
                )
                fonts.update(slide_fonts)
                consistency_records.append(consistency)
            _check_cross_slide_consistency(consistency_records, issues)
            report["summary"]["fonts"] = sorted(fonts)
            report["summary"]["chart_pages"] = chart_pages
    except zipfile.BadZipFile:
        _add_issue(issues, "error", "INVALID_ZIP", "File is not a readable PPTX/ZIP package.")
    except OSError as exc:
        _add_issue(issues, "error", "READ_ERROR", f"Cannot read PPTX: {exc}")

    return _finalize_report(report)


def _print_text(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(f"File: {report['file']}")
    print(
        "Slides: {slide_count} | Notes: {notes_count} | Blocking: {blocking} | "
        "Review: {review_required} | Advisories: {advisories} | Tool failures: {tool_failures}".format(
            **summary
        )
    )
    size = summary["slide_size_inches"]
    if size["width"] and size["height"]:
        print(f"Canvas: {size['width']} × {size['height']} in")
    if summary["fonts"]:
        print("Fonts: " + ", ".join(summary["fonts"]))
    for issue in report["issues"]:
        location = f" slide={issue['slide']}" if "slide" in issue else ""
        shape = issue.get("shape")
        if shape is not None:
            shape_id = shape.get("id")
            shape_name = shape.get("name", "")
            location += f" shape={shape_id}"
            if shape_name:
                location += f" name={shape_name!r}"
        print(f"[{issue['severity'].upper()}] {issue['code']}{location}: {issue['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run portable static checks on a PPTX package.")
    parser.add_argument("pptx", type=Path, help="Path to the PPTX file")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    parser.add_argument("--fail-on-error", action="store_true", help="Return exit code 2 when errors exist")
    parser.add_argument("--fail-on-review", action="store_true", help="Return exit code 4 when review is required")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return exit code 3 when warnings exist")
    parser.add_argument(
        "--expected-aspect-ratio",
        help="Expected slide ratio in W:H form, such as 16:9 or 4:3",
    )
    args = parser.parse_args(argv)

    report = validate_pptx(args.pptx, expected_aspect_ratio=args.expected_aspect_ratio)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_text(report)

    if report["summary"]["tool_failures"]:
        return 2
    if args.fail_on_error and report["summary"]["blocking"]:
        return 3
    if args.fail_on_review and report["summary"]["review_required"]:
        return 4
    if args.fail_on_warning and report["summary"]["warnings"]:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
