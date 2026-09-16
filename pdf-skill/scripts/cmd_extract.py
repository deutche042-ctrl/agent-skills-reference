"""Content extraction commands"""

import pdfplumber
import pikepdf
from pathlib import Path
from pdf import Output


def _parse_pages(pages_str: str, total: int) -> list:
    """Parse page range string

    Supported formats: "1", "1-3", "1,3,5", "1-3,5,7-9"
    Returns 0-indexed page number list
    """
    if not pages_str:
        return list(range(total))

    result = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start = int(start) - 1
            end = int(end)
            result.extend(range(start, min(end, total)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total:
                result.append(idx)

    return sorted(set(result))


def extract_text(pdf_path: str, pages: str = None):
    """Extract text"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pdfplumber.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    result = {
        "total_pages": len(pdf.pages),
        "extracted_pages": len(page_indices),
        "pages": []
    }

    total_chars = 0
    for idx in page_indices:
        page = pdf.pages[idx]
        text = page.extract_text() or ""
        total_chars += len(text)

        result["pages"].append({
            "page": idx + 1,
            "chars": len(text),
            "text": text
        })

    result["total_chars"] = total_chars

    if total_chars == 0:
        result["likely_scanned"] = True
        result["warning"] = (
            "No text content could be extracted from this PDF; it may be a scanned "
            "document (a pure-image PDF). Suggestions: 1) use an OCR tool (e.g. "
            "Tesseract) to recognize the text first; 2) or use the 'extract image' "
            "command to extract the images and then process them."
        )
    elif len(page_indices) > 0 and total_chars / len(page_indices) < 10:
        result["likely_scanned"] = True
        result["warning"] = (
            "Very little text was extracted per page from this PDF (average < 10 "
            "characters/page); it may contain many images or be partially scanned. "
            "Full content extraction may require OCR."
        )

    pdf.close()

    Output.success(result)


def extract_table(pdf_path: str, pages: str = None):
    """Extract tables"""
    path = Output.check_file(pdf_path)

    try:
        pdf = pdfplumber.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    page_indices = _parse_pages(pages, len(pdf.pages))

    result = {
        "total_pages": len(pdf.pages),
        "extracted_pages": len(page_indices),
        "tables": []
    }

    for idx in page_indices:
        page = pdf.pages[idx]
        tables = page.extract_tables()

        for i, table in enumerate(tables):
            if not table:
                continue

            # Clean table data
            cleaned = []
            for row in table:
                cleaned_row = [cell.strip() if cell else "" for cell in row]
                cleaned.append(cleaned_row)

            result["tables"].append({
                "page": idx + 1,
                "table_index": i,
                "rows": len(cleaned),
                "cols": len(cleaned[0]) if cleaned else 0,
                "data": cleaned
            })

    result["total_tables"] = len(result["tables"])
    pdf.close()

    Output.success(result)


def extract_image(pdf_path: str, output_dir: str):
    """Extract embedded images"""
    path = Output.check_file(pdf_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        Output.error("PDFError", f"Cannot open PDF: {e}", code=3)

    extracted = []
    image_count = 0

    for page_num, page in enumerate(pdf.pages, 1):
        # Get images from page resources
        if "/Resources" not in page:
            continue

        resources = page.Resources
        if "/XObject" not in resources:
            continue

        xobjects = resources.XObject
        for name, xobj in xobjects.items():
            try:
                if xobj.get("/Subtype") != "/Image":
                    continue
            except Exception:
                continue

            # image_count drives the filename; always increment so names stay
            # unique even when an individual image fails to extract.
            image_count += 1
            width = int(xobj.get("/Width", 0))
            height = int(xobj.get("/Height", 0))
            fileprefix = str(out_dir / f"page{page_num}_img{image_count}")

            saved_path = None
            fmt = None

            # Preferred path: let pikepdf decode the image and write a VALID file with
            # the correct extension (FlateDecode -> .png via Pillow, DCTDecode -> .jpg,
            # etc.). This replaces the old behavior of dumping the raw compressed stream,
            # which produced unopenable ".png" files for FlateDecode images.
            try:
                pdf_image = pikepdf.PdfImage(xobj)
                saved_path = pdf_image.extract_to(fileprefix=fileprefix)
                fmt = Path(saved_path).suffix.lstrip(".").lower()
            except Exception:
                # Fallback: write the raw stream only for formats whose raw bytes ARE a
                # self-contained file (JPEG / JPEG2000). For anything else, skip rather
                # than emit a corrupt file.
                try:
                    filter_str = str(xobj.get("/Filter", ""))
                    if "DCTDecode" in filter_str:
                        ext = "jpg"
                    elif "JPXDecode" in filter_str:
                        ext = "jp2"
                    else:
                        ext = None

                    if ext:
                        fallback_path = f"{fileprefix}.{ext}"
                        with open(fallback_path, "wb") as f:
                            f.write(xobj.read_raw_bytes())
                        saved_path = fallback_path
                        fmt = ext
                except Exception:
                    saved_path = None

            if not saved_path:
                # Could not extract this image in a valid format; skip it.
                continue

            extracted.append({
                "page": page_num,
                "name": str(name),
                "file": str(saved_path),
                "width": width,
                "height": height,
                "format": fmt
            })

    pdf.close()

    Output.success({
        "output_dir": str(out_dir),
        "total_images": len(extracted),
        "images": extracted
    })
