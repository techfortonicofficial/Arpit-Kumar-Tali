from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
FONT = "Calibri"


ET.register_namespace("w", NS_W)


def qn(local_name: str) -> str:
    return f"{{{NS_W}}}{local_name}"


def parse_markdown(md_text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            blocks.append(("title", line[2:].strip()))
        elif line.startswith("## "):
            blocks.append(("section", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("subhead", line[4:].strip()))
        elif line.startswith("- "):
            blocks.append(("bullet", line[2:].strip()))
        elif "Email:" in line and "Phone:" in line:
            blocks.append(("contact", line))
        elif re.fullmatch(r"\d{4} - (?:\d{4}|Present)", line) or " | " in line:
            blocks.append(("meta", line))
        else:
            blocks.append(("body", line))
    return blocks


def run(
    text: str,
    *,
    size_pt: float,
    color: str,
    bold: bool = False,
    italic: bool = False,
    caps: bool = False,
) -> ET.Element:
    r = ET.Element(qn("r"))
    r_pr = ET.SubElement(r, qn("rPr"))
    ET.SubElement(
        r_pr,
        qn("rFonts"),
        {
            qn("ascii"): FONT,
            qn("hAnsi"): FONT,
            qn("cs"): FONT,
        },
    )
    if bold:
        ET.SubElement(r_pr, qn("b"))
    if italic:
        ET.SubElement(r_pr, qn("i"))
    if caps:
        ET.SubElement(r_pr, qn("caps"))
    ET.SubElement(r_pr, qn("color"), {qn("val"): color})
    ET.SubElement(r_pr, qn("sz"), {qn("val"): str(int(round(size_pt * 2)))})

    t = ET.SubElement(r, qn("t"))
    if text[:1].isspace() or text[-1:].isspace():
        t.set(XML_SPACE, "preserve")
    t.text = text
    return r


def paragraph(
    text: str,
    *,
    size_pt: float,
    color: str,
    bold: bool = False,
    italic: bool = False,
    caps: bool = False,
    align: str | None = None,
    before: int = 0,
    after: int = 0,
    line: int = 240,
    left: int = 0,
    hanging: int = 0,
    keep_next: bool = False,
    border_bottom: bool = False,
) -> ET.Element:
    p = ET.Element(qn("p"))
    p_pr = ET.SubElement(p, qn("pPr"))
    if keep_next:
        ET.SubElement(p_pr, qn("keepNext"))

    spacing_attrs: dict[str, str] = {}
    if before:
        spacing_attrs[qn("before")] = str(before)
    if after:
        spacing_attrs[qn("after")] = str(after)
    if line:
        spacing_attrs[qn("line")] = str(line)
        spacing_attrs[qn("lineRule")] = "auto"
    if spacing_attrs:
        ET.SubElement(p_pr, qn("spacing"), spacing_attrs)

    if left or hanging:
        ind_attrs: dict[str, str] = {}
        if left:
            ind_attrs[qn("left")] = str(left)
        if hanging:
            ind_attrs[qn("hanging")] = str(hanging)
        ET.SubElement(p_pr, qn("ind"), ind_attrs)

    if align:
        ET.SubElement(p_pr, qn("jc"), {qn("val"): align})

    if border_bottom:
        p_bdr = ET.SubElement(p_pr, qn("pBdr"))
        ET.SubElement(
            p_bdr,
            qn("bottom"),
            {
                qn("val"): "single",
                qn("sz"): "6",
                qn("space"): "1",
                qn("color"): "D9DEE7",
            },
        )

    p.append(
        run(
            text,
            size_pt=size_pt,
            color=color,
            bold=bold,
            italic=italic,
            caps=caps,
        )
    )
    return p


def build_document_xml(md_path: Path) -> bytes:
    blocks = parse_markdown(md_path.read_text(encoding="utf-8"))

    document = ET.Element(qn("document"))
    body = ET.SubElement(document, qn("body"))

    for kind, text in blocks:
        if kind == "title":
            body.append(
                paragraph(
                    text,
                    size_pt=22,
                    color="111827",
                    bold=True,
                    align="center",
                    after=60,
                    line=260,
                )
            )
        elif kind == "contact":
            body.append(
                paragraph(
                    text,
                    size_pt=10,
                    color="64748B",
                    align="center",
                    after=160,
                    line=240,
                )
            )
        elif kind == "section":
            body.append(
                paragraph(
                    text.upper(),
                    size_pt=11.5,
                    color="0F766E",
                    bold=True,
                    caps=True,
                    before=180,
                    after=80,
                    line=240,
                    keep_next=True,
                    border_bottom=True,
                )
            )
        elif kind == "subhead":
            body.append(
                paragraph(
                    text,
                    size_pt=11,
                    color="111827",
                    bold=True,
                    before=60,
                    after=10,
                    line=240,
                    keep_next=True,
                )
            )
        elif kind == "meta":
            body.append(
                paragraph(
                    text,
                    size_pt=9.5,
                    color="64748B",
                    italic=True,
                    after=40,
                    line=220,
                )
            )
        elif kind == "bullet":
            body.append(
                paragraph(
                    "\u2022 " + text,
                    size_pt=9.8,
                    color="334155",
                    before=0,
                    after=14,
                    line=230,
                    left=540,
                    hanging=260,
                )
            )
        else:
            body.append(
                paragraph(
                    text,
                    size_pt=10,
                    color="334155",
                    after=60,
                    line=240,
                )
            )

    sect_pr = ET.SubElement(body, qn("sectPr"))
    ET.SubElement(sect_pr, qn("pgSz"), {qn("w"): "12240", qn("h"): "15840"})
    ET.SubElement(
        sect_pr,
        qn("pgMar"),
        {
            qn("top"): "1080",
            qn("right"): "1080",
            qn("bottom"): "1080",
            qn("left"): "1080",
            qn("header"): "720",
            qn("footer"): "720",
            qn("gutter"): "0",
        },
    )
    ET.SubElement(sect_pr, qn("cols"), {qn("space"): "720"})
    ET.SubElement(sect_pr, qn("docGrid"), {qn("linePitch"): "360"})

    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


def write_docx(template_path: Path, output_path: Path, document_xml: bytes) -> None:
    with zipfile.ZipFile(template_path, "r") as src:
        entries = {name: src.read(name) for name in src.namelist()}

    entries["word/document.xml"] = document_xml

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for name, data in entries.items():
            dst.writestr(name, data)


def main() -> None:
    md_path = Path("Arpit_Kumar_Tali_Resume.md")
    template_path = Path("Arpit_Kumar_Tali_Resume.docx")
    document_xml = build_document_xml(md_path)

    for output_name in ("Arpit_Kumar_Tali_Resume.docx", "resume.docx"):
        write_docx(template_path, Path(output_name), document_xml)
        print(f"Created {Path(output_name).resolve()}")


if __name__ == "__main__":
    main()
