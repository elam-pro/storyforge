from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    """Small semantic colour system shared by every StoryForge screen."""

    bg: str
    surface: str
    surface_raised: str
    sidebar: str
    text: str
    muted: str
    subtle: str
    border: str
    border_strong: str
    accent: str
    accent_hover: str
    accent_soft: str
    success: str
    danger: str
    input_bg: str
    selection: str


LIGHT = Palette(
    bg="#F1F1EE",
    surface="#FFFFFF",
    surface_raised="#F7F7F4",
    sidebar="#F7F7F4",
    text="#202220",
    muted="#686B67",
    subtle="#8B8E89",
    border="#DADCD7",
    border_strong="#C6C9C3",
    accent="#C8452F",
    accent_hover="#DA5138",
    accent_soft="#F5E1DB",
    success="#2D9F63",
    danger="#D84A44",
    input_bg="#FAFAF7",
    selection="#F2D3C9",
)


DARK = Palette(
    bg="#0D1112",
    surface="#15191A",
    surface_raised="#191E1F",
    sidebar="#111516",
    text="#F0F1EE",
    muted="#A4A7A3",
    subtle="#747975",
    border="#2B3131",
    border_strong="#3A4140",
    accent="#D04A33",
    accent_hover="#E0583D",
    accent_soft="#3B211C",
    success="#49B879",
    danger="#F15B4D",
    input_bg="#181D1E",
    selection="#5A2A21",
)


def stylesheet(p: Palette, editor_font_size: int = 15) -> str:
    """Return the complete Qt stylesheet for the selected appearance."""

    return f"""
    * {{ outline: none; }}
    QWidget {{
        color: {p.text};
        font-family: "Inter", "SF Pro Text", "Segoe UI", "Noto Sans", sans-serif;
        font-size: 13px;
    }}
    QMainWindow, QWidget#AppRoot, QWidget#PageHost {{ background: {p.bg}; }}
    QWidget#ChatCanvas {{ background: {p.surface}; }}
    QFrame#Sidebar {{
        background: {p.sidebar};
        border-right: 1px solid {p.border};
    }}
    QFrame#TopBar {{
        background: {p.sidebar};
        border-bottom: 1px solid {p.border};
    }}
    QFrame#Card, QFrame#Panel {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 3px;
    }}
    QFrame#Inset {{
        background: {p.surface_raised};
        border: 1px solid {p.border};
        border-radius: 3px;
    }}
    QFrame#Separator {{
        background: {p.border}; border: 0; min-height: 1px; max-height: 1px;
    }}
    QLabel#Brand {{ color: {p.text}; font-size: 15px; font-weight: 700; }}
    QLabel#BrandMark {{
        color: {p.accent}; background: transparent; border: 0;
        font-size: 16px; font-weight: 800;
    }}
    QLabel#TopTitle {{ color: {p.text}; font-size: 15px; font-weight: 650; }}
    QLabel#Kicker {{
        color: {p.accent}; font-size: 11px; font-weight: 700; letter-spacing: 1px;
    }}
    QLabel#PageTitle {{ color: {p.text}; font-size: 27px; font-weight: 700; }}
    QLabel#SectionTitle {{ color: {p.text}; font-size: 18px; font-weight: 650; }}
    QLabel#CardTitle {{ color: {p.text}; font-size: 14px; font-weight: 650; }}
    QLabel#Body {{ color: {p.text}; font-size: 13px; }}
    QLabel#Muted {{ color: {p.muted}; font-size: 12px; }}
    QLabel#Caption {{
        color: {p.muted}; font-size: 11px; font-weight: 700; letter-spacing: .4px;
    }}
    QLabel#Metric {{ color: {p.text}; font-size: 26px; font-weight: 700; }}
    QLabel#AccentPill {{
        color: {p.accent}; background: {p.accent_soft}; border-radius: 3px;
        padding: 4px 9px; font-size: 11px; font-weight: 650;
    }}
    QLabel#ProjectChip {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 3px; padding: 7px 9px; font-size: 12px;
    }}
    QPushButton {{
        min-height: 18px; padding: 8px 12px; border-radius: 3px;
        border: 1px solid transparent; font-size: 13px; font-weight: 600;
    }}
    QPushButton:hover {{ background: {p.surface_raised}; }}
    QPushButton[role="primary"] {{
        color: white; background: {p.accent}; border-color: {p.accent};
    }}
    QPushButton[role="primary"]:hover {{
        background: {p.accent_hover}; border-color: {p.accent_hover};
    }}
    QPushButton[role="primary"]:disabled {{
        color: {p.subtle}; background: {p.border}; border-color: {p.border};
    }}
    QPushButton[role="secondary"] {{
        color: {p.text}; background: {p.surface_raised}; border-color: {p.border};
    }}
    QPushButton[role="secondary"]:hover {{
        border-color: {p.border_strong}; background: {p.surface};
    }}
    QPushButton[role="tertiary"] {{
        color: {p.muted}; background: transparent; border-color: {p.border};
    }}
    QPushButton[role="tertiary"]:hover {{
        color: {p.text}; background: {p.surface_raised}; border-color: {p.border_strong};
    }}
    QPushButton[role="tertiary"]:disabled {{
        color: {p.subtle}; background: transparent; border-color: {p.border};
    }}
    QPushButton[role="quiet"] {{
        color: {p.muted}; background: transparent; padding: 7px 9px;
    }}
    QPushButton[role="quiet"]:hover {{
        color: {p.text}; background: {p.surface_raised};
    }}
    QPushButton[scriptElement="true"] {{
        color: {p.muted}; background: transparent; border-color: transparent;
    }}
    QPushButton[scriptElement="true"]:hover {{
        color: {p.text}; background: {p.surface_raised}; border-color: {p.border};
    }}
    QPushButton[scriptElement="true"]:checked {{
        color: {p.accent}; background: {p.accent_soft}; border-color: {p.accent};
        font-weight: 700;
    }}
    QPushButton#SidebarToggle {{
        color: {p.muted}; background: transparent; border: 1px solid transparent;
        padding: 0; font-size: 13px;
    }}
    QPushButton#SidebarToggle:hover {{
        color: {p.accent}; background: {p.accent_soft}; border-color: {p.border};
    }}
    QPushButton[role="danger"] {{
        color: {p.danger}; background: transparent; border-color: {p.danger};
    }}
    QPushButton[role="danger"]:hover {{
        color: white; background: {p.danger}; border-color: {p.danger};
    }}
    QPushButton[role="danger"]:disabled {{
        color: {p.subtle}; background: transparent; border-color: {p.border};
    }}
    QPushButton[nav="true"] {{
        color: {p.muted}; background: transparent; border: 0; border-radius: 4px;
        padding: 0;
    }}
    QLabel#NavIcon {{
        color: {p.muted}; background: transparent; border: 0;
        font-size: 17px; font-weight: 650;
    }}
    QLabel#NavLabel {{
        color: {p.muted}; background: transparent; border: 0;
        font-size: 14px; font-weight: 550;
    }}
    QLabel#NavIcon[navChild="true"], QLabel#NavLabel[navChild="true"] {{ color: {p.subtle}; }}
    QLabel#NavIcon[navActive="true"], QLabel#NavLabel[navActive="true"] {{
        color: {p.accent}; font-weight: 700;
    }}
    QPushButton[nav="true"]:hover {{
        color: {p.text}; background: {p.surface_raised};
    }}
    QPushButton[nav="true"]:checked {{
        color: {p.accent}; background: {p.accent_soft}; font-weight: 700;
    }}
    QPushButton[segment="true"] {{
        color: {p.muted}; background: transparent; border: 0; border-radius: 9px;
        padding: 8px 10px; text-align: left; font-weight: 550;
    }}
    QPushButton[segment="true"]:hover {{
        color: {p.text}; background: {p.surface_raised};
    }}
    QPushButton[segment="true"]:checked {{
        color: {p.accent}; background: {p.accent_soft}; font-weight: 650;
    }}
    QPushButton[studioTab="true"] {{
        color: {p.muted}; background: transparent; border: 0;
        border-radius: 0; min-height: 22px; padding: 6px 5px;
        text-align: left; font-size: 13px; font-weight: 600;
    }}
    QPushButton[studioTab="true"]:hover {{ color: {p.text}; background: {p.surface_raised}; }}
    QPushButton[studioTab="true"]:checked {{
        color: {p.text}; border-bottom: 2px solid {p.accent};
    }}
    QPushButton[synopsisQuestion="true"] {{
        min-height: 14px; padding: 3px 8px; border-radius: 7px;
    }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 3px; padding: 8px 10px; selection-background-color: {p.selection};
    }}
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {p.border_strong};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {p.accent};
    }}
    QTextEdit[editor="true"], QPlainTextEdit[editor="true"] {{
        font-family: "SF Pro Text", "Segoe UI", "Noto Sans", sans-serif;
        font-size: {editor_font_size}px; padding: 16px;
    }}
    QTextEdit#LearningAnswer {{
        background: {p.surface}; border: 1px solid {p.border_strong};
        border-radius: 16px; padding: 22px;
    }}
    QTextEdit#LearningAnswer:focus {{ border-color: {p.accent}; }}
    QLabel#CharacterPortrait, QLabel#LocationCover {{
        background: {p.surface_raised}; border: 1px solid {p.border}; border-radius: 3px;
        padding: 8px;
    }}
    QTabWidget::pane {{
        background: transparent; border: 0; border-top: 1px solid {p.border};
    }}
    QTabBar::tab {{
        color: {p.muted}; background: transparent; border: 0;
        padding: 10px 14px; font-size: 13px; font-weight: 600;
    }}
    QTabBar::tab:selected {{ color: {p.accent}; border-bottom: 2px solid {p.accent}; }}
    QTabBar::tab:hover {{ color: {p.text}; background: {p.surface_raised}; }}
    QTabWidget#CharacterTabs QTabBar::tab {{
        padding: 9px 9px; font-size: 12px;
    }}
    QComboBox::drop-down {{ border: 0; width: 24px; }}
    QComboBox QAbstractItemView {{
        color: {p.text}; background: {p.surface}; border: 1px solid {p.border};
        selection-background-color: {p.accent_soft}; selection-color: {p.text}; padding: 5px;
    }}
    QComboBox#ProjectChip {{
        color: {p.text}; background: {p.surface_raised}; border-color: {p.border};
        border-radius: 3px; padding: 6px 9px; font-size: 12px;
    }}
    QTreeWidget {{
        color: {p.text}; background: transparent; alternate-background-color: {p.surface_raised};
        border: 0; border-radius: 10px; selection-background-color: {p.accent_soft};
        selection-color: {p.text};
    }}
    QTreeWidget::item {{
        min-height: 38px; border-bottom: 1px solid {p.border}; padding: 2px 7px;
    }}
    QTreeWidget::item:hover {{ background: {p.surface_raised}; }}
    QTreeWidget#OutlineTree {{
        background: {p.surface}; alternate-background-color: {p.surface_raised};
        border: 1px solid {p.border}; border-radius: 14px;
    }}
    QTreeWidget#OutlineTree::item:selected {{
        color: {p.text}; background: {p.accent_soft};
    }}
    QListWidget#IdeaList {{
        color: {p.text}; background: transparent; border: 0; border-radius: 10px;
        selection-background-color: {p.accent_soft}; selection-color: {p.text};
    }}
    QListWidget#IdeaList::item {{
        min-height: 48px; border-bottom: 1px solid {p.border}; border-radius: 9px;
        padding: 8px 10px;
    }}
    QListWidget#IdeaList::item:hover {{ background: {p.surface_raised}; }}
    QListWidget#IdeaList::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border-left: 3px solid {p.accent};
    }}
    QListWidget#CharacterLibrary {{
        color: {p.text}; background: transparent; border: 0;
        selection-background-color: transparent;
    }}
    QListWidget#CharacterLibrary::item {{
        background: {p.surface_raised}; border: 1px solid {p.border}; border-radius: 11px;
        padding: 8px; margin: 2px;
    }}
    QListWidget#CharacterLibrary::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#CharacterLibrary::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border: 2px solid {p.accent};
    }}
    QListWidget#CharacterReferences {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 12px; padding: 5px; selection-background-color: transparent;
    }}
    QListWidget#CharacterReferences::item {{
        background: {p.surface}; border: 1px solid {p.border}; border-radius: 9px;
        padding: 5px; margin: 2px;
    }}
    QListWidget#CharacterReferences::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#CharacterReferences::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border: 2px solid {p.accent};
    }}
    QListWidget#CharacterRoster {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 12px; padding: 5px; selection-background-color: transparent;
    }}
    QListWidget#CharacterRoster::item {{
        background: {p.surface}; border: 1px solid transparent; border-radius: 9px;
        padding: 8px 9px; margin: 2px;
    }}
    QListWidget#CharacterRoster::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#CharacterRoster::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border-color: {p.accent};
    }}
    QListWidget#ArcCharacterList, QListWidget#StoryPromiseList, QListWidget#StoryMomentList {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 3px; padding: 5px; selection-background-color: transparent;
    }}
    QListWidget#ArcCharacterList::item, QListWidget#StoryPromiseList::item,
    QListWidget#StoryMomentList::item {{
        background: {p.surface}; border: 1px solid transparent; border-radius: 2px;
        padding: 8px 9px; margin: 2px;
    }}
    QListWidget#ArcCharacterList::item:hover, QListWidget#StoryPromiseList::item:hover,
    QListWidget#StoryMomentList::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#ArcCharacterList::item:selected, QListWidget#StoryPromiseList::item:selected,
    QListWidget#StoryMomentList::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border-color: {p.accent};
    }}
    QListWidget#LocationList, QListWidget#ThemePositionList, QListWidget#ThemeMotifList,
    QListWidget#ConflictList {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 12px; padding: 5px; selection-background-color: transparent;
    }}
    QListWidget#LocationList::item, QListWidget#ThemePositionList::item,
    QListWidget#ThemeMotifList::item, QListWidget#ConflictList::item {{
        background: {p.surface}; border: 1px solid transparent; border-radius: 9px;
        padding: 8px 9px; margin: 2px;
    }}
    QListWidget#LocationList::item:hover, QListWidget#ThemePositionList::item:hover,
    QListWidget#ThemeMotifList::item:hover, QListWidget#ConflictList::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#LocationList::item:selected, QListWidget#ThemePositionList::item:selected,
    QListWidget#ThemeMotifList::item:selected, QListWidget#ConflictList::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border-color: {p.accent};
    }}
    QListWidget#LocationImages {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 12px; padding: 5px; selection-background-color: transparent;
    }}
    QListWidget#LocationImages::item {{
        background: {p.surface}; border: 1px solid {p.border}; border-radius: 9px;
        padding: 5px; margin: 2px;
    }}
    QListWidget#LocationImages::item:hover {{ border-color: {p.border_strong}; }}
    QListWidget#LocationImages::item:selected {{
        color: {p.text}; background: {p.accent_soft}; border: 2px solid {p.accent};
    }}
    QListWidget#CharacterGroups, QListWidget#CharacterConnections {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 4px;
        selection-background-color: {p.accent_soft}; selection-color: {p.text};
    }}
    QListWidget#TimelineCharacterPicker {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 11px; padding: 5px; outline: 0;
    }}
    QListWidget#StoryCardCharacterPicker {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 11px; padding: 5px; outline: 0;
    }}
    QListWidget#StoryCardCharacterPicker::item {{
        color: {p.text}; background: {p.surface}; border: 1px solid {p.border};
        border-radius: 8px; min-height: 26px; padding: 6px 9px; margin: 2px;
    }}
    QListWidget#WorldConnectionPicker, QListWidget#LocationConnectionPicker,
    QListWidget#ThemeConnectionPicker, QListWidget#ConflictConnectionPicker,
    QListWidget#ArcConnectionPicker, QListWidget#PromiseConnectionPicker {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 4px; outline: 0;
    }}
    QListWidget#WorldConnectionPicker::item, QListWidget#LocationConnectionPicker::item,
    QListWidget#ThemeConnectionPicker::item, QListWidget#ConflictConnectionPicker::item,
    QListWidget#ArcConnectionPicker::item, QListWidget#PromiseConnectionPicker::item {{
        color: {p.text}; background: {p.surface}; border: 1px solid transparent;
        border-radius: 7px; min-height: 24px; padding: 5px 8px; margin: 1px;
    }}
    QListWidget#WorldConnectionPicker::item:hover, QListWidget#LocationConnectionPicker::item:hover,
    QListWidget#ThemeConnectionPicker::item:hover, QListWidget#ConflictConnectionPicker::item:hover,
    QListWidget#ArcConnectionPicker::item:hover, QListWidget#PromiseConnectionPicker::item:hover {{
        background: {p.accent_soft}; border-color: {p.accent};
    }}
    QListWidget#LocationConnectionPicker::item {{
        min-height: 32px; padding: 7px 9px;
    }}
    QListWidget#LocationConnectionPicker::indicator {{
        width: 20px; height: 20px;
    }}
    QDialog#StoryCardDialog QTextEdit#StoryCardContent {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 11px; padding: 12px;
    }}
    QDialog#StoryCardDialog QTextEdit#StoryCardContent:focus {{ border-color: {p.accent}; }}
    QListWidget#TimelineCharacterPicker::item {{
        color: {p.text}; background: {p.surface}; border: 1px solid {p.border};
        border-radius: 8px; min-height: 26px; padding: 6px 9px; margin: 2px;
    }}
    QListWidget#TimelineCharacterPicker::item:hover {{
        background: {p.accent_soft}; border-color: {p.accent};
    }}
    QTableWidget#CharacterCustomTable {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; gridline-color: {p.border};
        selection-background-color: {p.accent_soft}; selection-color: {p.text};
    }}
    QLineEdit[characterField="true"], QTextEdit[characterField="true"],
    QComboBox[characterField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 8px 10px;
    }}
    QLineEdit[characterField="true"]:hover, QTextEdit[characterField="true"]:hover,
    QComboBox[characterField="true"]:hover {{ border-color: {p.border_strong}; }}
    QLineEdit[characterField="true"]:focus, QTextEdit[characterField="true"]:focus,
    QComboBox[characterField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit[arcField="true"], QComboBox[arcField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 3px; padding: 8px 10px;
    }}
    QTextEdit[arcField="true"]:hover, QComboBox[arcField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[arcField="true"]:focus, QComboBox[arcField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit[promiseField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 3px; padding: 8px 10px;
    }}
    QTextEdit[promiseField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[promiseField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit[sceneField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 3px; padding: 8px 10px;
    }}
    QTextEdit[sceneField="true"]:hover {{ border-color: {p.subtle}; }}
    QTextEdit[sceneField="true"]:focus {{ border-color: {p.accent}; }}
    QListWidget#SceneCharacterPicker, QListWidget#SceneConnectionPicker {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 3px; padding: 4px; outline: 0;
    }}
    QListWidget#SceneCharacterPicker::item, QListWidget#SceneConnectionPicker::item {{
        min-height: 26px; padding: 5px 7px; margin: 1px;
    }}
    QListWidget#SceneCharacterPicker::item:hover, QListWidget#SceneConnectionPicker::item:hover {{
        background: {p.surface_raised};
    }}
    QListWidget#SceneCharacterPicker::item:selected, QListWidget#SceneConnectionPicker::item:selected {{
        color: {p.text}; background: {p.accent_soft};
    }}
    QTextEdit[universeField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 10px 12px;
    }}
    QTextEdit[universeField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[universeField="true"]:focus {{ border-color: {p.accent}; }}
    QListWidget#SequenceList {{
        color: {p.text}; background: transparent; border: 0; outline: 0;
        selection-background-color: transparent;
    }}
    QListWidget#SequenceList::item {{
        background: transparent; border: 0; padding: 0;
    }}
    QListWidget#SequenceList::item:selected {{ background: transparent; }}
    QListWidget#ImageLibrary, QListWidget#ScriptScenes {{
        color: {p.text}; background: transparent; border: 0;
        selection-background-color: {p.accent_soft}; selection-color: {p.text};
    }}
    QListWidget#ImageLibrary::item {{
        background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 12px; padding: 8px;
    }}
    QListWidget#ImageLibrary::item:hover, QListWidget#ImageLibrary::item:selected {{
        border-color: {p.accent}; background: {p.accent_soft};
    }}
    QListWidget#ScriptScenes::item {{
        min-height: 36px; border-bottom: 1px solid {p.border};
        border-radius: 8px; padding: 5px 7px;
    }}
    QListWidget#ScriptScenes::item:hover {{ background: {p.surface_raised}; }}
    QListWidget#ScriptScenes::item:selected {{ background: {p.accent_soft}; color: {p.accent}; }}
    QFrame#SequenceBlock {{
        background: {p.surface}; border: 1px solid {p.border}; border-radius: 14px;
    }}
    QFrame#SequenceBlock:hover {{ border-color: {p.border_strong}; }}
    QLabel#SequenceHandle {{
        color: {p.subtle}; background: {p.surface_raised}; border: 1px solid {p.border};
        border-radius: 8px; font-size: 20px; font-weight: 700;
    }}
    QLabel#SequenceHandle:hover {{ color: {p.accent}; border-color: {p.accent}; }}
    QHeaderView::section {{
        color: {p.subtle}; background: transparent; border: 0; border-bottom: 1px solid {p.border};
        padding: 8px 7px; font-size: 11px; font-weight: 650;
    }}
    QScrollArea, QAbstractScrollArea {{ border: 0; background: transparent; }}
    QTextEdit[locationField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 10px; padding: 10px 12px;
    }}
    QTextEdit[locationField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[locationField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit[themeField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 10px 12px;
    }}
    QTextEdit[themeField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[themeField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit[conflictField="true"] {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 10px 12px;
    }}
    QTextEdit[conflictField="true"]:hover {{ border-color: {p.border_strong}; }}
    QTextEdit[conflictField="true"]:focus {{ border-color: {p.accent}; }}
    QTextEdit#IdeaEditor {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border};
        border-radius: 10px; padding: 12px 14px;
    }}
    QTextEdit#IdeaEditor:hover {{ border-color: {p.border_strong}; }}
    QTextEdit#IdeaEditor:focus {{ border-color: {p.accent}; }}
    QTextEdit#ScriptEditor {{
        color: {p.text}; background: {p.surface}; border: 1px solid {p.border_strong};
        border-radius: 12px; padding: 26px 34px;
        font-family: "Courier Prime", "Courier New", monospace;
        font-size: {editor_font_size}px;
    }}
    QTextEdit#ScriptEditor:focus {{ border-color: {p.accent}; }}
    QTableWidget#SceneTable {{
        color: {p.text}; background: {p.surface}; alternate-background-color: {p.surface_raised};
        border: 1px solid {p.border}; border-radius: 12px;
        gridline-color: {p.border}; selection-background-color: {p.accent_soft};
        selection-color: {p.text};
    }}
    QTableWidget#SceneTable::item {{ padding: 8px; }}
    QTableWidget#ArcOverview, QTableWidget#PromiseControlTable {{
        color: {p.text}; background: {p.surface}; alternate-background-color: {p.surface_raised};
        border: 1px solid {p.border}; border-radius: 3px; gridline-color: {p.border};
        selection-background-color: {p.accent_soft}; selection-color: {p.text};
    }}
    QTableWidget#ArcOverview::item, QTableWidget#PromiseControlTable::item {{ padding: 9px; }}
    QTableWidget#SceneTable QLineEdit {{
        min-height: 32px; padding: 7px 10px; margin: 3px;
        background: {p.input_bg}; border: 1px solid {p.accent}; border-radius: 8px;
    }}
    QLabel#AttachmentPreview {{
        color: {p.muted}; background: {p.surface}; border: 1px solid {p.border};
        border-radius: 10px; font-size: 13px; font-weight: 650;
    }}
    QLabel#AttachmentPreview:hover {{ color: {p.accent}; border-color: {p.accent}; }}
    QFrame#IdeaImageDrop {{
        background: {p.surface_raised}; border: 1px solid {p.border}; border-radius: 12px;
    }}
    QScrollArea#PanelScroll, QWidget#PanelCanvas {{
        background: {p.surface}; border: 0;
    }}
    QGraphicsView#StoryMapCanvas {{
        background: {p.surface_raised}; border: 1px solid {p.border_strong};
        border-radius: 14px;
    }}
    QGraphicsView#RelationshipMapCanvas {{
        background: {p.surface_raised}; border: 1px solid {p.border_strong};
        border-radius: 14px;
    }}
    QGraphicsView#TimelineCanvas {{
        background: {p.surface_raised}; border: 1px solid {p.border_strong};
        border-radius: 14px;
    }}
    QDialog#TimelineEventDialog {{ background: {p.bg}; }}
    QDialog#TimelineEventDialog QLineEdit,
    QDialog#TimelineEventDialog QTextEdit,
    QDialog#TimelineEventDialog QComboBox,
    QDialog#TimelineEventDialog QDoubleSpinBox {{
        color: {p.text}; background: {p.input_bg}; border: 1px solid {p.border_strong};
        border-radius: 10px; padding: 9px 11px;
    }}
    QDialog#TimelineEventDialog QLineEdit:focus,
    QDialog#TimelineEventDialog QTextEdit:focus,
    QDialog#TimelineEventDialog QComboBox:focus,
    QDialog#TimelineEventDialog QDoubleSpinBox:focus {{ border-color: {p.accent}; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{
        background: {p.border_strong}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{
        background: {p.border_strong}; border-radius: 4px; min-width: 30px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
    QProgressBar {{
        background: {p.border}; border: 0; border-radius: 3px;
    }}
    QProgressBar::chunk {{
        background: {p.accent}; border-radius: 3px;
    }}
    QCheckBox, QRadioButton {{ color: {p.text}; spacing: 9px; padding: 4px 0; }}
    QCheckBox::indicator, QRadioButton::indicator {{ width: 17px; height: 17px; }}
    QToolTip {{
        color: {p.text}; background: {p.surface_raised}; border: 1px solid {p.border}; padding: 6px;
    }}

    /* Compact studio shell and deliberately square working surfaces. */
    QScrollArea#NavScroll, QWidget#SidebarNav {{
        background: {p.sidebar}; border: 0;
    }}
    QFrame#NavSeparator {{
        background: {p.border}; border: 0; margin: 4px 8px;
        min-height: 1px; max-height: 1px;
    }}
    QFrame#ProjectSelector {{ border-radius: 3px; }}
    QListWidget#CharacterRoster, QListWidget#CharacterReferences,
    QListWidget#LocationList, QListWidget#LocationImages,
    QListWidget#ThemePositionList, QListWidget#ThemeMotifList,
    QListWidget#ConflictList, QListWidget#CharacterGroups,
    QListWidget#CharacterConnections, QListWidget#TimelineCharacterPicker,
    QListWidget#StoryCardCharacterPicker, QListWidget#WorldConnectionPicker,
    QListWidget#LocationConnectionPicker, QListWidget#ThemeConnectionPicker,
    QListWidget#ConflictConnectionPicker, QTableWidget#CharacterCustomTable,
    QTableWidget#SceneTable, QTreeWidget#OutlineTree,
    QGraphicsView#StoryMapCanvas, QGraphicsView#RelationshipMapCanvas,
    QGraphicsView#TimelineCanvas, QTextEdit#ScriptEditor,
    QTextEdit#LearningAnswer, QLabel#AttachmentPreview,
    QFrame#IdeaImageDrop, QFrame#SequenceBlock {{
        border-radius: 3px;
    }}
    QListWidget#CharacterRoster::item, QListWidget#CharacterReferences::item,
    QListWidget#LocationList::item, QListWidget#LocationImages::item,
    QListWidget#ThemePositionList::item, QListWidget#ThemeMotifList::item,
    QListWidget#ConflictList::item, QListWidget#ImageLibrary::item,
    QListWidget#ScriptScenes::item {{ border-radius: 2px; }}
    QTabBar::tab {{ padding: 9px 11px; font-size: 13px; }}
    QTabWidget#CharacterTabs QTabBar::tab {{ padding: 8px 8px; font-size: 13px; }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ border-radius: 2px; }}
    QDialog {{ background: {p.bg}; }}
    QFrame[message="assistant"] {{
        background: {p.surface_raised}; border: 1px solid {p.border}; border-radius: 3px;
    }}
    QFrame[message="user"] {{
        background: {p.accent_soft}; border: 1px solid {p.accent_soft}; border-radius: 3px;
    }}

    /* A single, restrained geometry for every work surface. */
    QPushButton, QPushButton[segment="true"], QPushButton[synopsisQuestion="true"],
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTreeWidget, QListWidget, QTableWidget, QGraphicsView,
    QLabel#CharacterPortrait, QLabel#LocationCover, QLabel#AttachmentPreview,
    QFrame#Card, QFrame#Panel, QFrame#Inset, QFrame#IdeaImageDrop,
    QFrame#SequenceBlock, QFrame[message="assistant"], QFrame[message="user"] {{
        border-radius: 3px;
    }}
    QLineEdit[characterField="true"], QTextEdit[characterField="true"],
    QComboBox[characterField="true"], QTextEdit[arcField="true"],
    QComboBox[arcField="true"], QTextEdit[promiseField="true"],
    QTextEdit[sceneField="true"], QTextEdit[universeField="true"],
    QTextEdit[locationField="true"], QTextEdit[themeField="true"],
    QTextEdit[conflictField="true"], QTextEdit#IdeaEditor,
    QTextEdit#ScriptEditor, QDialog#StoryCardDialog QTextEdit#StoryCardContent,
    QDialog#TimelineEventDialog QLineEdit, QDialog#TimelineEventDialog QTextEdit,
    QDialog#TimelineEventDialog QComboBox, QDialog#TimelineEventDialog QDoubleSpinBox {{
        border-radius: 3px;
    }}
    QTreeWidget::item, QListWidget::item {{ border-radius: 2px; }}
    """
