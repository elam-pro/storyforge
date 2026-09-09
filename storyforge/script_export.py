from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from xml.etree import ElementTree as ET

SCENE_PREFIXES = ("INT.", "EXT.", "INT./EXT.", "EXT./INT.", "I/E.")


def parse_screenplay(text: str) -> list[tuple[str, str]]:
    """Convert a lightweight Fountain-style draft into screenplay elements."""
    elements: list[tuple[str, str]] = []
    previous_type = ""
    previous_blank = True
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            previous_blank = True
            continue
        upper = line.upper()
        if upper.startswith(SCENE_PREFIXES):
            element_type = "Scene Heading"
            line = upper
        elif line.startswith("@"):
            element_type = "Character"
            line = line[1:].strip().upper()
        elif line.startswith("(") and line.endswith(")"):
            element_type = "Parenthetical"
        elif upper.endswith((" TO:", " À :", " A :")) or upper in {
            "CUT TO:", "FADE IN:", "FADE OUT.", "FONDU :",
        }:
            element_type = "Transition"
            line = upper
        elif line.startswith("!"):
            element_type = "Action"
            line = line[1:].lstrip()
        elif previous_type in {"Character", "Dialogue", "Parenthetical"} and not previous_blank:
            element_type = "Dialogue"
        elif previous_blank and line == upper and len(line) <= 42:
            element_type = "Character"
        else:
            element_type = "Action"
        elements.append((element_type, line))
        previous_type = element_type
        previous_blank = False
    return elements


def import_fdx(path: Path) -> str:
    """Read the screenplay body of a Final Draft XML file."""
    root = ET.parse(path).getroot()
    paragraphs = root.findall("./Content/Paragraph") or root.findall(".//Content/Paragraph")
    output: list[str] = []
    previous_type = ""
    for paragraph in paragraphs:
        paragraph_type = paragraph.attrib.get("Type", "Action")
        value = "".join(paragraph.itertext()).strip()
        if not value:
            continue
        if paragraph_type == "Scene Heading":
            value = value.upper()
        elif paragraph_type == "Character":
            value = f"@{value.upper()}"
        elif paragraph_type == "Action":
            value = f"!{value}"
        elif paragraph_type == "Parenthetical" and not value.startswith("("):
            value = f"({value.strip('()')})"
        elif paragraph_type == "Transition":
            value = value.upper()
        if output:
            compact_pair = paragraph_type in {"Dialogue", "Parenthetical"} and previous_type in {
                "Character", "Parenthetical", "Dialogue",
            }
            output.append("\n" if compact_pair else "\n\n")
        output.append(value)
        previous_type = paragraph_type
    return "".join(output).strip()


def import_fdx_document(path: Path, project_id=None):
    """Import supported paragraph kinds without guessing from their text.

    Inline styling/revisions are not a lossless Final Draft round trip.
    Unknown paragraph types are rejected rather than silently flattened.
    """
    from .screenplay_model import BlockType, ScreenplayBlock, ScreenplayDocument
    root = ET.parse(path).getroot()
    if root.tag != 'FinalDraft':
        raise ValueError('Document Final Draft attendu')
    kinds = dict(zip(('Scene Heading', 'Action', 'Character', 'Dialogue', 'Parenthetical', 'Transition'),
                    (BlockType.SCENE, BlockType.ACTION, BlockType.CHARACTER, BlockType.DIALOGUE, BlockType.PARENTHETICAL, BlockType.TRANSITION)))
    blocks = []
    for paragraph in root.findall('./Content/Paragraph'):
        kind = paragraph.get('Type', 'Action')
        if kind not in kinds:
            raise ValueError(f'Type FDX non pris en charge : {kind}')
        text = ''.join(''.join(node.itertext()) for node in paragraph.findall('Text'))
        blocks.append(ScreenplayBlock(type=kinds[kind], text=text))
    return ScreenplayDocument(metadata={'project_id': str(project_id)}, blocks=blocks)


def export_fdx(
    path: Path,
    title: str,
    text: str,
    author: str = "",
    contact: str = "",
    draft_date: str = "",
    *,
    elements: list[tuple[str, str]] | None = None,
    based_on: str = "",
    copyright_notice: str = "",
    include_title_page: bool = True,
) -> None:
    root = ET.Element(
        "FinalDraft",
        {"DocumentType": "Script", "Template": "No", "Version": "1"},
    )
    if include_title_page:
        title_page = ET.SubElement(root, "TitlePage")
        title_content = ET.SubElement(title_page, "Content")
        for paragraph_type, value in (
            ("Title", title), ("Author", author), ("Contact", contact),
            ("Draft", draft_date), ("Based On", based_on), ("Copyright", copyright_notice),
        ):
            if value:
                paragraph = ET.SubElement(title_content, "Paragraph", {"Type": paragraph_type})
                ET.SubElement(paragraph, "Text").text = value
    content = ET.SubElement(root, "Content")
    for element_type, value in (elements if elements is not None else parse_screenplay(text)):
        paragraph = ET.SubElement(content, "Paragraph", {"Type": element_type})
        ET.SubElement(paragraph, "Text").text = value
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _pdf_escape(value: str) -> str:
    encoded = value.encode("cp1252", "replace").decode("latin1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
SCRIPT_TOP = 720
SCRIPT_BOTTOM = 54
SCRIPT_LEADING = 12
COURIER_CHAR_WIDTH = 7.2


def _screenplay_lines(element_type: str, value: str) -> list[str]:
    widths = {
        "Scene Heading": 58,
        "Action": 60,
        "Character": 32,
        "Dialogue": 36,
        "Parenthetical": 26,
        "Transition": 28,
    }
    normalized = value.strip()
    if element_type in {"Scene Heading", "Character", "Transition"}:
        normalized = normalized.upper()
    return wrap(
        normalized,
        width=widths.get(element_type, 60),
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
    ) or [""]


def _element_x(element_type: str, value: str = "") -> float:
    if element_type in {"Scene Heading", "Action"}:
        return 108.0  # 1.5 inch left margin.
    if element_type == "Character":
        return 266.0
    if element_type == "Dialogue":
        return 180.0
    if element_type == "Parenthetical":
        return 223.0
    if element_type == "Transition":
        return max(360.0, 540.0 - len(value) * COURIER_CHAR_WIDTH)
    return 108.0


def _layout_screenplay_pages(
    elements: list[tuple[str, str]],
) -> list[list[tuple[float, float, str, bool]]]:
    """Lay out a screenplay on US Letter pages using industry-style indents."""

    pages: list[list[tuple[float, float, str, bool]]] = [[]]
    y = float(SCRIPT_TOP)

    def new_page() -> None:
        nonlocal y
        pages.append([])
        y = float(SCRIPT_TOP)

    def ensure(height: float) -> None:
        if pages[-1] and y - height < SCRIPT_BOTTOM:
            new_page()

    def draw(element_type: str, line: str, bold: bool = False) -> None:
        nonlocal y
        if y < SCRIPT_BOTTOM + SCRIPT_LEADING:
            new_page()
        pages[-1].append((_element_x(element_type, line), y, line, bold))
        y -= SCRIPT_LEADING

    index = 0
    while index < len(elements):
        element_type, value = elements[index]

        if element_type == "Character":
            cue = value.strip().lstrip("@").strip().upper()
            dialogue_group: list[tuple[str, str]] = []
            lookahead = index + 1
            while lookahead < len(elements) and elements[lookahead][0] in {
                "Parenthetical",
                "Dialogue",
            }:
                dialogue_group.append(elements[lookahead])
                lookahead += 1

            first_content_lines = 0
            for grouped_type, grouped_value in dialogue_group:
                first_content_lines += min(2, len(_screenplay_lines(grouped_type, grouped_value)))
                if first_content_lines >= 2:
                    break
            required = 12 + 12 + max(1, first_content_lines) * SCRIPT_LEADING
            ensure(required)
            if y < SCRIPT_TOP:
                y -= 12
            draw("Character", cue)

            for grouped_type, grouped_value in dialogue_group:
                lines = _screenplay_lines(grouped_type, grouped_value)
                for line_index, line in enumerate(lines):
                    if y < SCRIPT_BOTTOM + SCRIPT_LEADING:
                        if grouped_type == "Dialogue" and line_index < len(lines):
                            pages[-1].append((266.0, SCRIPT_BOTTOM, "(MORE)", False))
                        new_page()
                        continued = cue.removesuffix(" (CONT'D)").strip()
                        draw("Character", f"{continued} (CONT'D)")
                    draw(grouped_type, line)
            y -= 12
            index = lookahead
            continue

        lines = _screenplay_lines(element_type, value)
        before = 0 if not pages[-1] else 12
        if element_type == "Scene Heading":
            before = 0 if not pages[-1] else 24
            following_lines = 0
            if index + 1 < len(elements):
                next_type, next_value = elements[index + 1]
                following_lines = min(2, len(_screenplay_lines(next_type, next_value)))
            ensure(before + (len(lines) + following_lines) * SCRIPT_LEADING + 12)
        else:
            ensure(before + len(lines) * SCRIPT_LEADING)
        y -= before
        for line in lines:
            draw(element_type, line)
        if element_type in {"Scene Heading", "Action", "Transition"}:
            y -= 12
        index += 1

    return pages


def _centered_x(value: str, font_size: float = 12.0) -> float:
    return max(72.0, (PAGE_WIDTH - len(value) * font_size * 0.6) / 2.0)


def _wrapped_input_lines(value: str, width: int) -> list[str]:
    lines: list[str] = []
    for raw_line in value.splitlines() or [value]:
        lines.extend(
            wrap(
                raw_line,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or ([""] if raw_line == "" else [raw_line])
        )
    return lines


def _title_page_commands(
    title: str,
    author: str,
    contact: str,
    draft_date: str,
    based_on: str,
    copyright_notice: str,
) -> list[str]:
    commands = ["BT"]
    title_lines = wrap(
        (title or "SCÉNARIO SANS TITRE").upper(),
        width=42,
        break_long_words=False,
        break_on_hyphens=False,
    ) or ["SCÉNARIO SANS TITRE"]
    y = 510.0 + max(0, len(title_lines) - 1) * 9
    commands.append("/F2 12 Tf")
    for line in title_lines:
        commands.extend(
            [f"1 0 0 1 {_centered_x(line):.1f} {y:.1f} Tm", f"({_pdf_escape(line)}) Tj"]
        )
        y -= 18
    if author:
        y -= 18
        commands.extend(
            [
                "/F1 12 Tf",
                f"1 0 0 1 {_centered_x('Écrit par'):.1f} {y:.1f} Tm",
                f"({_pdf_escape('Écrit par')}) Tj",
            ]
        )
        y -= 18
        commands.extend(
            [f"1 0 0 1 {_centered_x(author):.1f} {y:.1f} Tm", f"({_pdf_escape(author)}) Tj"]
        )
    if based_on:
        y -= 30
        for line in _wrapped_input_lines(based_on, 46):
            commands.extend(
                [f"1 0 0 1 {_centered_x(line):.1f} {y:.1f} Tm", f"({_pdf_escape(line)}) Tj"]
            )
            y -= 15

    commands.append("/F1 10 Tf")
    contact_y = 118.0
    for line in _wrapped_input_lines(contact, 46) if contact else []:
        commands.extend([f"1 0 0 1 72 {contact_y:.1f} Tm", f"({_pdf_escape(line)}) Tj"])
        contact_y -= 13
    if copyright_notice:
        for line in _wrapped_input_lines(copyright_notice, 52):
            commands.extend([f"1 0 0 1 72 {contact_y:.1f} Tm", f"({_pdf_escape(line)}) Tj"])
            contact_y -= 13
    if draft_date:
        date_x = max(360.0, 540.0 - len(draft_date) * 6.0)
        commands.extend(
            [f"1 0 0 1 {date_x:.1f} 118 Tm", f"({_pdf_escape(draft_date)}) Tj"]
        )
    commands.append("ET")
    return commands


def export_script_pdf(
    path: Path,
    title: str,
    text: str,
    author: str = "",
    contact: str = "",
    draft_date: str = "",
    *,
    based_on: str = "",
    copyright_notice: str = "",
    include_title_page: bool = True,
    elements: list[tuple[str, str]] | None = None,
) -> None:
    """Write a professional US Letter screenplay PDF with safe pagination."""
    screenplay_elements = elements if elements is not None else parse_screenplay(text)
    pages = _layout_screenplay_pages(screenplay_elements)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        '\n'.join([title, author, contact, draft_date, based_on, copyright_notice] + [value for _, value in screenplay_elements]).encode('cp1252')
    except UnicodeEncodeError:
        from .unicode_script_pdf import render
        render(path, pages, title, author, contact, draft_date, based_on, copyright_notice, include_title_page)
        return

    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    regular_font = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
    )
    bold_font = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>"
    )
    content_ids: list[int] = []
    if include_title_page:
        title_commands = _title_page_commands(
            title,
            author,
            contact,
            draft_date,
            based_on,
            copyright_notice,
        )
        title_stream = "\n".join(title_commands).encode("latin1", "replace")
        content_ids.append(
            add(
                f"<< /Length {len(title_stream)} >>\nstream\n".encode()
                + title_stream
                + b"\nendstream"
            )
        )

    for page_number, page in enumerate(pages, start=1):
        commands = ["BT", "/F1 12 Tf"]
        for x, y, value, bold in page:
            commands.extend(
                [
                    f"/{'F2' if bold else 'F1'} 12 Tf",
                    f"1 0 0 1 {x:.1f} {y:.1f} Tm",
                    f"({_pdf_escape(value)}) Tj",
                ]
            )
        if page_number > 1:
            number = f"{page_number}."
            number_x = 540.0 - len(number) * 6.0
            commands.extend(
                [
                    "/F1 10 Tf",
                    f"1 0 0 1 {number_x:.1f} 756 Tm",
                    f"({_pdf_escape(number)}) Tj",
                ]
            )
        commands.append("ET")
        stream = "\n".join(commands).encode("latin1", "replace")
        content_ids.append(add(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"))

    pages_id = len(objects) + 1
    objects.append(b"")
    page_ids = []
    for content_id in content_ids:
        page_ids.append(add((
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {regular_font} 0 R /F2 {bold_font} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode()))
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    catalog = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(output)
    output += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        output += f"{offset:010d} 00000 n \n".encode()
    output += (
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\n"
        f"startxref\n{xref}\n%%EOF"
    ).encode()
    path.write_bytes(output)
