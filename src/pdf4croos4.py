#!/usr/bin/env python3
"""
4-up A4-landscape PDF creator with:

• tiny page numbers in the bottom-right of each mini-page
• the source PDF’s (stem) name centred on the top margin of every sheet

External dependencies
---------------------
pip install pypdf        # for PDF I/O + transforms          (tested on 5.9)
pip install reportlab    # to draw the page-number / header  (tested on 4.2)
"""

from pathlib import Path
import sys, io
from pypdf import PdfReader, PdfWriter, PageObject, Transformation   # ← external
from reportlab.pdfgen import canvas                                 # ← external

# ── geometry constants ─────────────────────────────────────────────
MM_TO_PT = 72 / 25.4                     # 1 mm → points
A4_W, A4_H = 297 * MM_TO_PT, 210 * MM_TO_PT            # A4 landscape (pts)
CELL_W, CELL_H = A4_W / 2, A4_H / 2                    # quadrant
CELL_ORIGINS = (                                       # TL, TR, BL, BR
    (0,      CELL_H),
    (CELL_W, CELL_H),
    (0,      0),
    (CELL_W, 0),
)

# ── stamp caches ───────────────────────────────────────────────────
_stamp_cache: dict[int, PageObject] = {}       # page-number stamps
_header_cache: dict[str, PageObject] = {}      #  header by filename


def number_stamp(n: int) -> PageObject:
    """CELL-sized transparent page with tiny number n bottom-right."""
    if n in _stamp_cache:
        return _stamp_cache[n]

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(CELL_W, CELL_H))
    c.setFont("Helvetica", 7)
    c.drawRightString(CELL_W - 4, 4, str(n))   # 4 pt inset
    c.save()
    buf.seek(0)

    _stamp_cache[n] = PdfReader(buf).pages[0]
    return _stamp_cache[n]


def header_stamp(doc_stem: str) -> PageObject:
    """Full-A4 transparent page with filename centred at the very top."""
    if doc_stem in _header_cache:
        return _header_cache[doc_stem]

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(A4_W, A4_H))
    c.setFont("Helvetica-Bold", 9)
    text_y = A4_H - 10                    # 10 pt down from top edge
    c.drawCentredString(A4_W / 2, text_y, doc_stem)
    c.save()
    buf.seek(0)

    _header_cache[doc_stem] = PdfReader(buf).pages[0]
    return _header_cache[doc_stem]


# ── main 4-up routine ──────────────────────────────────────────────
def make_4up(reader: PdfReader, doc_stem: str) -> PdfWriter:
    writer = PdfWriter()

    for i in range(0, len(reader.pages), 4):
        sheet = PageObject.create_blank_page(width=A4_W, height=A4_H)

        # add filename header once per sheet
        sheet.merge_page(header_stamp(doc_stem))

        # add up to four mini-pages + page numbers
        for j, (cell_x, cell_y) in enumerate(CELL_ORIGINS):
            idx = i + j
            if idx >= len(reader.pages):
                break

            pg = reader.pages[idx]
            sw, sh = float(pg.mediabox.width), float(pg.mediabox.height)

            scale = min(CELL_W / sw, CELL_H / sh)
            dx = cell_x + (CELL_W - sw * scale) / 2
            dy = cell_y + (CELL_H - sh * scale) / 2

            sheet.merge_transformed_page(
                pg,
                Transformation().scale(scale).translate(dx, dy)
            )

            sheet.merge_transformed_page(
                number_stamp(idx + 1),
                Transformation().translate(cell_x, cell_y)
            )

        writer.add_page(sheet)

    return writer


# ── command-line entry point ───────────────────────────────────────
def main(inp: Path, out: Path) -> None:
    reader = PdfReader(str(inp))
    writer = make_4up(reader, inp.stem)
    with out.open("wb") as fh:
        writer.write(fh)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python pdf_4up_a4_numbers_header.py input.pdf output.pdf")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
