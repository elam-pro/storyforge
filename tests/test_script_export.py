from pathlib import Path
from xml.etree import ElementTree as ET

from script_export import (
    _layout_screenplay_pages,
    export_fdx,
    export_script_pdf,
    import_fdx,
    parse_screenplay,
)

SCRIPT = """INT. MUSÉE - NUIT

!Mina referme la porte derrière elle.

@MINA
(à voix basse)
Le tableau a bougé.

COUPE À :

EXT. MUSÉE - AUBE

Le jour révèle une fenêtre ouverte.
"""


def test_screenplay_parser_and_exports(tmp_path: Path) -> None:
    elements = parse_screenplay(SCRIPT)
    assert elements[0] == ("Scene Heading", "INT. MUSÉE - NUIT")
    assert ("Character", "MINA") in elements
    assert ("Parenthetical", "(à voix basse)") in elements
    assert ("Dialogue", "Le tableau a bougé.") in elements
    assert ("Transition", "COUPE À :") in elements

    fdx_path = tmp_path / "scenario.fdx"
    pdf_path = tmp_path / "scenario.pdf"
    export_fdx(fdx_path, "Le tableau", SCRIPT, "Camille", "camille@example.test", "Version 2")
    export_script_pdf(pdf_path, "Le tableau", SCRIPT, "Camille", "camille@example.test", "Version 2")

    root = ET.parse(fdx_path).getroot()
    assert root.tag == "FinalDraft"
    paragraph_types = [item.attrib["Type"] for item in root.findall("./Content/Paragraph")]
    assert "Scene Heading" in paragraph_types
    assert "Dialogue" in paragraph_types
    assert root.findtext("./TitlePage/Content/Paragraph/Text") == "Le tableau"
    imported = import_fdx(fdx_path)
    assert "INT. MUSÉE - NUIT" in imported
    assert "@MINA" in imported
    assert "Le tableau a bougé." in imported
    assert pdf_path.read_bytes().startswith(b"%PDF-1.4")
    assert pdf_path.stat().st_size > 500

    metadata_fdx = tmp_path / "metadata.fdx"
    export_fdx(
        metadata_fdx,
        "Le tableau",
        SCRIPT,
        "Camille",
        based_on="Une histoire originale",
        copyright_notice="Copyright 2026 Camille",
    )
    metadata_root = ET.parse(metadata_fdx).getroot()
    title_page_values = {
        paragraph.attrib["Type"]: paragraph.findtext("Text")
        for paragraph in metadata_root.findall("./TitlePage/Content/Paragraph")
    }
    assert title_page_values["Based On"] == "Une histoire originale"
    assert title_page_values["Copyright"] == "Copyright 2026 Camille"

    no_title_fdx = tmp_path / "without_title.fdx"
    export_fdx(no_title_fdx, "Le tableau", SCRIPT, include_title_page=False)
    assert ET.parse(no_title_fdx).getroot().find("TitlePage") is None


def test_pdf_uses_screenplay_indents_and_optional_title_page(tmp_path: Path) -> None:
    elements = parse_screenplay(SCRIPT)
    page = _layout_screenplay_pages(elements)[0]
    by_text = {text: x for x, _y, text, _bold in page}
    assert by_text["INT. MUSÉE - NUIT"] == 108.0
    assert by_text["MINA"] == 266.0
    assert by_text["Le tableau a bougé."] == 180.0
    assert by_text["(à voix basse)"] == 223.0
    assert by_text["COUPE À :"] >= 360.0

    with_title = tmp_path / "with_title.pdf"
    export_script_pdf(
        with_title,
        "Le tableau",
        SCRIPT,
        "Camille Martin",
        "camille@example.test",
        "Version du 29 août 2026",
        based_on="Une histoire originale",
        copyright_notice="Copyright 2026 Camille Martin",
    )
    payload = with_title.read_bytes()
    assert payload.count(b"/Type /Page ") == 2
    assert b"(LE TABLEAU)" in payload
    assert b"(Camille Martin)" in payload
    assert b"(INT. MUS" in payload

    without_title = tmp_path / "without_title.pdf"
    export_script_pdf(
        without_title,
        "Le tableau",
        SCRIPT,
        include_title_page=False,
    )
    assert without_title.read_bytes().count(b"/Type /Page ") == 1


def test_long_dialogue_continues_cleanly_on_the_next_page(tmp_path: Path) -> None:
    long_dialogue = " ".join(["Cette réplique doit continuer sans sortir de la page."] * 120)
    elements = [
        ("Scene Heading", "INT. SALLE - NUIT"),
        ("Character", "MINA"),
        ("Dialogue", long_dialogue),
    ]
    output = tmp_path / "continued.pdf"
    export_script_pdf(
        output,
        "Dialogue long",
        "",
        include_title_page=False,
        elements=elements,
    )
    payload = output.read_bytes()
    assert payload.count(b"/Type /Page ") > 1
    assert b"\\(MORE\\)" in payload
    assert b"(MINA \\(CONT'D\\))" in payload
