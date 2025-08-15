# src/fll_sim/scripts/fetch_mat.py
from __future__ import annotations

from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover - runtime check
    requests = None

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional dependency
    fitz = None

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    Image = None

ALLOWED_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "application/octet-stream": ".png",  # some servers mislabel; save as .png
}


def fetch_mat_image(
    url: str, out_path: Path, *, timeout: float = 20.0
) -> Path:
    """
    Download a mat image from a user-provided URL and save to out_path.
    Returns out_path.

    Note: Caller must supply the URL. This function does not hardcode or fetch
    any URLs by itself.
    """
    if requests is None:
        raise ImportError(
            "requests library not installed. Install with: "
            "pip install requests"
        )

    out_path = out_path.with_suffix(out_path.suffix or ".png")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # If already exists and non-empty, no-op
    if out_path.exists() and out_path.stat().st_size > 0:
        return out_path

    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()

    ctype = r.headers.get("Content-Type", "").split(";")[0].strip().lower()
    ext = ALLOWED_CONTENT_TYPES.get(ctype, None)

    # If we can infer from URL extension, honor that
    if not ext:
        for cand in (".png", ".jpg", ".jpeg"):
            if url.lower().endswith(cand):
                ext = cand
                break
    if not ext:
        # Fallback to PNG
        ext = ".png"

    out_path = out_path.with_suffix(ext)

    with open(out_path, "wb") as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)

    return out_path


def fetch_mat_pdf(
    url: str,
    out_path: Path,
    *,
    page: int = 0,
    dpi: int = 300,
    timeout: float = 30.0,
) -> Path:
    """
    Download a PDF mat from a user-provided URL, rasterize a page to PNG, and
    save to out_path (PNG). Returns out_path.

    Requires PyMuPDF (imported as fitz) and Pillow.
    """
    if requests is None:
        raise ImportError(
            "requests library not installed. Install with: "
            "pip install requests"
        )
    if fitz is None:
        raise ImportError(
            "PyMuPDF not installed. Install with: pip install PyMuPDF"
        )
    if Image is None:
        raise ImportError(
            "Pillow not installed. Install with: pip install Pillow"
        )

    out_path = out_path.with_suffix(".png")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # If already exists and non-empty, no-op
    if out_path.exists() and out_path.stat().st_size > 0:
        return out_path

    # Download PDF into memory
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    pdf_bytes = r.content

    # Open with PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if page < 0 or page >= doc.page_count:
        raise ValueError(
            "Page index {page} out of range for PDF with "
            f"{doc.page_count} pages"
        )
    pg = doc.load_page(page)

    # Compute matrix for DPI
    zoom = dpi / 72.0  # 72 DPI is base
    mat = fitz.Matrix(zoom, zoom)
    pix = pg.get_pixmap(matrix=mat, alpha=False)

    # Convert pixmap to PIL Image and save as PNG
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.save(out_path, format="PNG")

    return out_path
