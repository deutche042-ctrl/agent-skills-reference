# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Convert a .docx file to .pdf.

Usage:
    uv run scripts/docx_to_pdf.py input.docx
    uv run scripts/docx_to_pdf.py input.docx -o output.pdf
    uv run scripts/docx_to_pdf.py input.docx -o /tmp/output.pdf

When -o is not specified, the PDF is output to the same directory as the input file, with the same name but a .pdf extension.
Depends on LibreOffice (soffice), with zero Python third-party dependencies.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# mapping table from Windows Chinese font names → Linux-available font names
# when LibreOffice on Linux cannot find a Windows font it shows garbled text, so replace them beforehand
_FONT_MAP = {
    "宋体": "Noto Serif CJK SC",
    "SimSun": "Noto Serif CJK SC",
    "新宋体": "Noto Serif CJK SC",
    "NSimSun": "Noto Serif CJK SC",
    "黑体": "Noto Sans CJK SC",
    "SimHei": "Noto Sans CJK SC",
    "微软雅黑": "Noto Sans CJK SC",
    "Microsoft YaHei": "Noto Sans CJK SC",
    "楷体": "WenQuanYi Zen Hei",
    "KaiTi": "WenQuanYi Zen Hei",
    "仿宋": "WenQuanYi Zen Hei",
    "FangSong": "WenQuanYi Zen Hei",
    "等线": "Noto Sans CJK SC",
    "DengXian": "Noto Sans CJK SC",
}


def _patch_fonts(src: Path, dst: Path) -> None:
    """Batch-replace the Windows Chinese font names in the docx's XML with Linux-available font names."""
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                text = data.decode("utf-8")
                for win_font, linux_font in _FONT_MAP.items():
                    text = text.replace(win_font, linux_font)
                data = text.encode("utf-8")
            zout.writestr(item, data)


def convert(docx_path: str, output_path: str | None = None) -> Path:
    src = Path(docx_path)
    if not src.exists():
        print(f"Error: file does not exist: {src}", file=sys.stderr)
        sys.exit(1)
    if src.suffix.lower() not in (".docx", ".doc"):
        print(f"Error: not a Word file: {src}", file=sys.stderr)
        sys.exit(1)

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("Error: LibreOffice (soffice) not found, please install it first", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt install libreoffice-nogui", file=sys.stderr)
        print("  macOS: brew install --cask libreoffice", file=sys.stderr)
        sys.exit(1)

    if output_path:
        out = Path(output_path)
        outdir = out.parent
        outdir.mkdir(parents=True, exist_ok=True)
    else:
        out = src.with_suffix(".pdf")
        outdir = src.parent

    env = dict(os.environ)
    # in some environments harfbuzz and freetype have a symbol conflict that needs LD_PRELOAD to fix
    freetype = Path("/usr/lib/x86_64-linux-gnu/libfreetype.so.6")
    if freetype.exists():
        env.setdefault("LD_PRELOAD", str(freetype))
    lo_prog = Path("/usr/lib/libreoffice/program")
    if lo_prog.is_dir():
        env["LD_LIBRARY_PATH"] = str(lo_prog) + ":" + env.get("LD_LIBRARY_PATH", "")

    with tempfile.TemporaryDirectory() as tmpdir:
        # write to a temp file after replacing fonts, to avoid modifying the original file
        patched = Path(tmpdir) / src.name
        _patch_fonts(src, patched)

        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmpdir, str(patched)],
            capture_output=True, text=True, env=env,
        )

        if result.returncode != 0:
            print("Error: LibreOffice conversion failed", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(1)

        generated = Path(tmpdir) / f"{src.stem}.pdf"
        if not generated.exists():
            print(f"Error: PDF file not found after conversion: {generated}", file=sys.stderr)
            sys.exit(1)

        shutil.move(str(generated), str(out))

    kb = out.stat().st_size / 1024
    print(f"Generated: {out} ({kb:.1f} KB)")
    return out


def main():
    parser = argparse.ArgumentParser(description="Convert a .docx to .pdf")
    parser.add_argument("docx_path", help=".docx file path")
    parser.add_argument("-o", "--output", help="output .pdf path (defaults to the same directory and name as the input)")
    args = parser.parse_args()
    convert(args.docx_path, args.output)


if __name__ == "__main__":
    main()
