"""Format conversion commands"""

import subprocess
import shutil
from pathlib import Path
from pdf import Output


# Supported input formats
SUPPORTED_FORMATS = {
    # Office documents
    ".docx", ".doc", ".odt", ".rtf",
    # Presentations
    ".pptx", ".ppt", ".odp",
    # Spreadsheets
    ".xlsx", ".xls", ".ods", ".csv",
    # Other
    ".txt", ".html", ".htm",
}


def _find_libreoffice() -> str:
    """Find LibreOffice executable"""
    # macOS
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
    ]
    for p in mac_paths:
        if Path(p).exists():
            return p

    # Linux / generic
    if shutil.which("soffice"):
        return "soffice"
    if shutil.which("libreoffice"):
        return "libreoffice"

    return None


def convert_to_pdf(input_path: str, output_path: str = None):
    """Convert file to PDF"""
    path = Output.check_file(input_path)

    # Check format support
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        Output.error(
            "UnsupportedFormat",
            f"Unsupported format: {suffix}",
            hint=f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Find LibreOffice
    soffice = _find_libreoffice()
    if not soffice:
        Output.error(
            "DependencyMissing",
            "LibreOffice not found",
            hint="Please install LibreOffice: https://www.libreoffice.org/download/",
            code=2,
        )

    # Determine output path
    if output_path:
        out_dir = Path(output_path).parent
        out_name = Path(output_path).stem
    else:
        out_dir = path.parent
        out_name = path.stem

    out_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

    except subprocess.TimeoutExpired:
        Output.error("Timeout", "Conversion timeout (>120s)", code=4)
    except Exception as e:
        Output.error("ConvertError", f"Conversion failed: {e}", code=4)

    # LibreOffice output filename is fixed to original_name.pdf
    generated_pdf = out_dir / f"{path.stem}.pdf"

    # IMPORTANT: LibreOffice frequently exits with code 0 even when it fails (e.g. it
    # prints "Error: source file could not be loaded" to stdout and still returns 0).
    # So detect failure by a non-zero return code OR the expected PDF not existing,
    # and surface a clean structured error instead of letting the rename() below raise
    # a raw FileNotFoundError traceback.
    combined = ((result.stdout or "") + (result.stderr or "")).strip()
    if result.returncode != 0 or not generated_pdf.exists():
        last_line = combined.splitlines()[-1] if combined else "Unknown error"
        Output.error(
            "ConvertError",
            f"LibreOffice could not convert the file: {last_line}",
            hint="Ensure the input is a valid, non-corrupt document and LibreOffice is fully installed.",
            code=4,
        )

    # If a different output name was specified, move to it (copy+unlink handles the
    # cross-filesystem case where rename() would raise EXDEV).
    if output_path and Path(output_path).name != generated_pdf.name:
        final_path = Path(output_path)
        try:
            generated_pdf.rename(final_path)
        except OSError:
            shutil.copyfile(generated_pdf, final_path)
            generated_pdf.unlink(missing_ok=True)
    else:
        final_path = generated_pdf

    if not final_path.exists():
        Output.error("ConvertError", "Converted PDF file was not generated", code=4)

    Output.success({
        "input": str(path),
        "output": str(final_path),
        "format": suffix
    })
