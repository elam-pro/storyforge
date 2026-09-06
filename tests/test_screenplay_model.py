from screenplay_model import BlockType, ScreenplayBlock, ScreenplayDocument


def test_legacy_script_migrates_to_typed_blocks_and_public_elements() -> None:
    document = ScreenplayDocument.from_legacy_text(
        "INT. HALL - JOUR\n\n!Mina avance.\n\n@MINA\n(à voix basse)\nJe reste."
    )

    assert [block.type for block in document.blocks if block.text.strip()] == [
        BlockType.SCENE,
        BlockType.ACTION,
        BlockType.CHARACTER,
        BlockType.PARENTHETICAL,
        BlockType.DIALOGUE,
    ]
    assert next(block.text for block in document.blocks if block.type is BlockType.CHARACTER) == "MINA"
    assert document.elements()[-1] == ("Dialogue", "Je reste.")


def test_empty_document_starts_on_a_scene_heading() -> None:
    document = ScreenplayDocument.from_legacy_text("")

    assert len(document.blocks) == 1
    assert document.blocks[0].type is BlockType.SCENE
    assert document.to_plain_text() == ""


def test_json_round_trip_preserves_document_and_block_ids() -> None:
    document = ScreenplayDocument.from_legacy_text("INT. HALL - JOUR\n\nMINA")
    document.set_block_type(2, BlockType.CHARACTER)
    document.blocks[2].metadata["source"] = "legacy-editor"
    block_ids = [block.id for block in document.blocks]

    restored = ScreenplayDocument.from_json(document.to_json())

    assert restored is not None
    assert restored.document_id == document.document_id
    assert [block.id for block in restored.blocks] == block_ids
    assert restored.blocks[2].metadata["source"] == "legacy-editor"
    assert restored.to_plain_text() == document.to_plain_text()


def test_editor_sync_keeps_ids_for_edits_and_adds_ids_for_new_blocks() -> None:
    document = ScreenplayDocument.from_legacy_text("INT. HALL - JOUR\n\nMINA\nJe reste.")
    original_ids = [block.id for block in document.blocks]

    document.sync_from_editor(
        [
            ("INT. HALL - JOUR", BlockType.SCENE),
            ("", BlockType.ACTION),
            ("MINA", BlockType.CHARACTER),
            ("Je pars.", BlockType.DIALOGUE),
            ("", BlockType.ACTION),
        ]
    )

    assert document.blocks[0].id == original_ids[0]
    assert document.blocks[2].id == original_ids[2]
    assert document.blocks[3].id == original_ids[3]
    assert document.blocks[3].text == "Je pars."
    assert document.blocks[4].id not in original_ids


def test_rename_character_preserves_continued_cue() -> None:
    document = ScreenplayDocument(
        blocks=[
            ScreenplayBlock(text="MINA", type=BlockType.CHARACTER),
            ScreenplayBlock(text="MINA (CONT'D)", type=BlockType.CHARACTER),
            ScreenplayBlock(text="MINA", type=BlockType.DIALOGUE),
        ]
    )

    assert document.rename_character("Mina", "Julian") == 2
    assert [block.text for block in document.blocks] == [
        "JULIAN",
        "JULIAN (CONT'D)",
        "MINA",
    ]
