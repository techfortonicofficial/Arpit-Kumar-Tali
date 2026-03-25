from __future__ import annotations

import re
from pathlib import Path
from textwrap import wrap


PAGE_W = 612.0
PAGE_H = 792.0
MARGIN_L = 54.0
MARGIN_R = 54.0
MARGIN_T = 54.0
MARGIN_B = 54.0
USABLE_W = PAGE_W - MARGIN_L - MARGIN_R
TOP_Y = PAGE_H - MARGIN_T


class LineItem:
    def __init__(self, font: str, size: float, x: float, y: float, text: str) -> None:
        self.font = font
        self.size = size
        self.x = x
        self.y = y
        self.text = text


class Layout:
    def __init__(self) -> None:
        self.pages: list[list[LineItem]] = [[]]
        self.y = TOP_Y

    def new_page(self) -> None:
        self.pages.append([])
        self.y = TOP_Y

    def ensure_space(self, height: float) -> None:
        if self.y - height < MARGIN_B:
            self.new_page()

    def add_line(
        self,
        text: str,
        *,
        font: str,
        size: float,
        x: float,
        center: bool = False,
        leading: float | None = None,
    ) -> None:
        wrapped = wrap_text(text, size)
        line_h = leading if leading is not None else max(size * 1.25, 11.0)

        for chunk in wrapped:
            if center:
                text_w = len(chunk) * size * 0.52
                x_pos = max(MARGIN_L, (PAGE_W - text_w) / 2.0)
            else:
                x_pos = x

            self.ensure_space(line_h)
            self.pages[-1].append(LineItem(font, size, x_pos, self.y, chunk))
            self.y -= line_h


def wrap_text(text: str, size: float) -> list[str]:
    if not text:
        return [""]

    max_chars = max(30, int(USABLE_W / (size * 0.52)))
    return wrap(text, width=max_chars, break_long_words=False, break_on_hyphens=False) or [""]


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_layout(md_path: Path) -> Layout:
    layout = Layout()
    lines = md_path.read_text(encoding="utf-8").splitlines()

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            layout.y -= 5.0
            if layout.y < MARGIN_B:
                layout.new_page()
            continue

        if stripped.startswith("# "):
            layout.add_line(stripped[2:].strip(), font="F2", size=20.0, x=MARGIN_L, center=True, leading=22.0)
            layout.y -= 2.0
            continue

        if stripped.startswith("## "):
            layout.y -= 9.0
            layout.add_line(stripped[3:].strip().upper(), font="F2", size=12.0, x=MARGIN_L, leading=14.0)
            layout.y -= 2.0
            continue

        if stripped.startswith("### "):
            layout.y -= 4.0
            layout.add_line(stripped[4:].strip(), font="F2", size=10.5, x=MARGIN_L, leading=12.0)
            layout.y -= 1.0
            continue

        if stripped.startswith("- "):
            layout.add_line(stripped, font="F1", size=10.0, x=MARGIN_L + 8.0, leading=12.0)
            continue

        if "Email:" in stripped and "Phone:" in stripped:
            layout.add_line(stripped, font="F1", size=10.0, x=MARGIN_L, center=True, leading=12.0)
            layout.y -= 1.0
            continue

        if " | " in stripped or re.fullmatch(r"\d{4} - (\d{4}|Present)", stripped):
            layout.add_line(stripped, font="F3", size=9.5, x=MARGIN_L, leading=11.0)
            continue

        layout.add_line(stripped, font="F1", size=10.0, x=MARGIN_L, leading=12.0)

    return layout


def build_pdf(layout: Layout, out_path: Path) -> None:
    fonts = [
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-BoldOblique >>",
    ]

    objects: list[str] = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")

    kid_ids = []
    for i in range(len(layout.pages)):
        page_id = 8 + i * 2
        kid_ids.append(f"{page_id} 0 R")
    objects.append(f"<< /Type /Pages /Kids [{' '.join(kid_ids)}] /Count {len(layout.pages)} >>")
    objects.extend(fonts)

    for i, page in enumerate(layout.pages):
        content_parts = ["BT"]
        for line in page:
            content_parts.append(f"/{line.font} {line.size:.1f} Tf")
            content_parts.append(f"1 0 0 1 {line.x:.2f} {line.y:.2f} Tm")
            content_parts.append(f"({pdf_escape(line.text)}) Tj")
        content_parts.append("ET")
        content = "\n".join(content_parts)
        content_bytes = content.encode("utf-8")
        content_id = 7 + i * 2
        page_id = content_id + 1
        objects.append(f"<< /Length {len(content_bytes)} >>\nstream\n{content}\nendstream")
        objects.append(
            "<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {int(PAGE_W)} {int(PAGE_H)}] "
            "/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("ascii"))
        pdf.extend(obj.encode("utf-8"))
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    pdf.extend(b"startxref\n")
    pdf.extend(f"{xref_start}\n".encode("ascii"))
    pdf.extend(b"%%EOF\n")

    out_path.write_bytes(pdf)


def main() -> None:
    md_path = Path("Arpit_Kumar_Tali_Resume.md")
    out_path = Path("Arpit_Kumar_Tali_Resume.pdf")
    layout = build_layout(md_path)
    build_pdf(layout, out_path)
    print(f"Created {out_path.resolve()} with {len(layout.pages)} page(s)")


if __name__ == "__main__":
    main()
