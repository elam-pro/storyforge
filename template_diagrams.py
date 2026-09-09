"""Native structural diagrams; positions illustrate a model, never grade a story."""
import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


DIAGRAM_FAMILIES = {
    "causal_spine": "causal-ladder",
    "short_film": "film-strip",
    "three_acts": "three-arches",
    "four_movements": "four-quadrants",
    "story_circle": "story-circle",
    "eight_sequences": "sequence-snake",
    "hero_journey": "outward-return",
    "kishotenketsu": "contrast-diamond",
    "mystery": "clue-convergence",
    "relationship": "relationship-braid",
    "mckee_value_progression": "value-wave",
    "truby_seven_steps": "seven-facets",
    "save_the_cat": "beat-lanes",
}


def build_diagram(template, palette, parent=None):
    view = QGraphicsView(parent)
    scene = QGraphicsScene(view)
    view.setScene(scene)
    view.setObjectName("TemplateVisualCanvas")
    view.setProperty("diagramFamily", DIAGRAM_FAMILIES[template["key"]])
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    steps, key = template["steps"], template["key"]
    accent = QColor(palette.accent)
    guide_pen = QPen(QColor(palette.border_strong), 2)
    guide_pen.setCosmetic(True)
    def label(text, x, y, width=190, muted=False):
        item = scene.addText(text)
        item.setTextWidth(width)
        item.setDefaultTextColor(QColor(palette.muted if muted else palette.text))
        item.setPos(x, y)
        return item
    label(template["title"], 20, 10, 900)
    label("Repères facultatifs · survole un point pour ses détails · glisse pour explorer", 20, 45, 900, True)
    label_positions = []
    if key == "story_circle":
        cx, cy, radius = 420, 390, 225
        scene.addEllipse(cx-radius, cy-radius, radius*2, radius*2, QPen(accent, 3))
        label("DÉPART\n↓\nEXPÉRIENCE\n↓\nRETOUR TRANSFORMÉ", cx-90, cy-65, 180)
        positions = [(cx + radius*math.cos(-math.pi/2+i*math.tau/len(steps)),
                      cy + radius*math.sin(-math.pi/2+i*math.tau/len(steps))) for i in range(len(steps))]
        label_positions = [
            (x + 18 if x >= cx else x - 205, y - 35) for x, y in positions
        ]
    elif key == "causal_spine":
        positions = [(90 + i * 145, 245 + (i % 2) * 210) for i in range(len(steps))]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for x, y in positions[1:]:
            path.lineTo(x, y)
        scene.addPath(path, QPen(accent, 4))
        label("CAUSE", 55, 155, 120, True)
        label("↓ CONSÉQUENCE ↓", 405, 360, 210, True)
        label("NOUVELLE CAUSE", 815, 545, 180, True)
        label_positions = [(x - 60, y - 92 if i % 2 == 0 else y + 28) for i, (x, y) in enumerate(positions)]
    elif key == "short_film":
        positions = [(90 + i * 170, 355) for i in range(len(steps))]
        strip = QPainterPath()
        strip.addRoundedRect(QRectF(35, 260, 930, 190), 28, 28)
        scene.addPath(strip, guide_pen)
        for x in range(60, 950, 55):
            scene.addEllipse(x, 275, 12, 12, guide_pen)
            scene.addEllipse(x, 425, 12, 12, guide_pen)
        for first, second in zip(positions, positions[1:]):
            scene.addLine(*first, *second, QPen(accent, 3))
        scene.addLine(positions[0][0], 225, positions[-1][0], 225, guide_pen)
        label("UNE SITUATION · UNE DÉCISION · UNE IMAGE FINALE", 255, 185, 560, True)
        label_positions = [(x - 65, 315 if i % 2 == 0 else 370) for i, (x, _y) in enumerate(positions)]
    elif key == "three_acts":
        positions = [(105, 475), (300, 310), (510, 405), (720, 265), (930, 455)]
        for caption, left, width in (
            ("ACTE I · INSTALLER", 45, 300),
            ("ACTE II · DÉVELOPPER", 350, 430),
            ("ACTE III · RÉSOUDRE", 785, 205),
        ):
            label(caption, left, 135, width, True)
            scene.addLine(left, 175, left + width - 18, 175, guide_pen)
        path = QPainterPath()
        path.moveTo(*positions[0])
        for index in range(1, len(positions), 2):
            end = positions[min(index + 1, len(positions) - 1)]
            peak = positions[index]
            path.quadTo(peak[0], peak[1] - 80, end[0], end[1])
        scene.addPath(path, QPen(accent, 4))
        label_positions = [(x - 70, y + 28 if i % 2 == 0 else y - 105) for i, (x, y) in enumerate(positions)]
    elif key == "four_movements":
        positions = [(250, 230), (650, 230), (650, 580), (250, 580)]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:] + positions[:1]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        scene.addLine(450, 200, 450, 610, guide_pen)
        scene.addLine(220, 405, 680, 405, guide_pen)
        label("1 → 2 · première direction", 300, 155, 310, True)
        label("3 → 4 · nouvelle direction", 300, 635, 310, True)
        label_positions = [(x - 205 if x < 450 else x + 25, y - 30) for x, y in positions]
    elif key == "eight_sequences":
        top = [(90 + i * 235, 275) for i in range(4)]
        bottom = [(795 - i * 235, 570) for i in range(4)]
        positions = top + bottom
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        label("PREMIÈRE MOITIÉ →", 45, 185, 390, True)
        label("← SECONDE MOITIÉ", 510, 650, 390, True)
        label_positions = [(x - 72, y - 78 if i < 4 else y + 25) for i, (x, y) in enumerate(positions)]
    elif key == "hero_journey":
        positions = [(75, 535), (250, 390), (425, 245), (600, 245), (775, 390), (950, 535)]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        scene.addLine(75, 590, 950, 590, guide_pen)
        label("MONDE CONNU", 35, 620, 180, True)
        label("INCONNU · ÉPREUVES · CHOIX", 370, 155, 350, True)
        label("RETOUR TRANSFORMÉ", 800, 620, 220, True)
        label_positions = [(x - 65, y + 25 if i in {0, 5} else y - 92) for i, (x, y) in enumerate(positions)]
    elif key == "kishotenketsu":
        positions = [(220, 245), (650, 245), (650, 570), (220, 570)]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:] + positions[:1]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        scene.addLine(220, 245, 650, 570, guide_pen)
        scene.addLine(650, 245, 220, 570, guide_pen)
        label("CONTRASTE", 370, 370, 160, True)
        label_positions = [(x - 185 if x < 400 else x + 22, y - 32) for x, y in positions]
    elif key == "mystery":
        center = (520, 420)
        positions = [(135, 220), (320, 590), (470, 185), (700, 610), (875, 250), center]
        for point in positions[:-1]:
            scene.addLine(*point, *center, guide_pen)
        scene.addEllipse(center[0] - 58, center[1] - 58, 116, 116, QPen(accent, 3))
        label("INDICES ET HYPOTHÈSES", 35, 105, 300, True)
        label("RÉVÉLATION\n→ nouvelle décision", center[0] - 85, center[1] - 22, 175)
        label_positions = [(x - 75, y - 80) for x, y in positions[:-1]] + [(center[0] + 75, center[1] + 20)]
    elif key == "relationship":
        positions = [(90, 285), (260, 520), (430, 285), (600, 520), (770, 285), (940, 520)]
        upper = QPainterPath()
        lower = QPainterPath()
        upper.moveTo(90, 320)
        lower.moveTo(90, 485)
        for i in range(1, len(positions)):
            x = positions[i][0]
            upper.quadTo(x - 85, 210 if i % 2 else 395, x, 320 if i % 2 == 0 else 485)
            lower.quadTo(x - 85, 595 if i % 2 else 405, x, 485 if i % 2 == 0 else 320)
        scene.addPath(upper, QPen(accent, 4))
        scene.addPath(lower, guide_pen)
        label("DEUX ATTENTES", 35, 160, 230, True)
        label("FRICTIONS · OUVERTURES · ÉPREUVES", 340, 650, 420, True)
        label_positions = [(x - 70, y - 82 if i % 2 == 0 else y + 25) for i, (x, y) in enumerate(positions)]
    elif key == "mckee_value_progression":
        positions = [(90, 250), (265, 500), (440, 205), (615, 555), (790, 165), (965, 405)]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        scene.addLine(45, 360, 1000, 360, guide_pen)
        label("VALEUR POSITIVE", 35, 105, 220, True)
        label("VALEUR NÉGATIVE / CONTRAIRE", 35, 650, 300, True)
        label_positions = [(x - 65, y - 85 if y < 360 else y + 25) for x, y in positions]
    elif key == "truby_seven_steps":
        cx, cy, radius = 470, 405, 245
        positions = [
            (cx + radius * math.cos(-math.pi / 2 + i * math.tau / len(steps)),
             cy + radius * math.sin(-math.pi / 2 + i * math.tau / len(steps)))
            for i in range(len(steps))
        ]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for point in positions[1:] + positions[:1]:
            path.lineTo(*point)
        scene.addPath(path, QPen(accent, 4))
        label("DÉSIR", cx - 45, cy - 70, 100, True)
        label("↕", cx - 10, cy - 25, 40)
        label("TRANSFORMATION", cx - 95, cy + 25, 210, True)
        label_positions = [(x + 18 if x >= cx else x - 205, y - 35) for x, y in positions]
    elif key == "save_the_cat":
        # Three act lanes, with the longer middle act split at the midpoint.
        # This is a reading map, not a forced percentage/page calculator.
        positions = []
        for caption, first, last, y in (("ACTE I · INSTALLATION",0,5,220),
                                      ("ACTE II · EXPLORATION",5,9,450),
                                      ("ACTE II · PRESSION ET COMPRÉHENSION",9,13,680),
                                      ("ACTE III · RÉSOLUTION",13,15,910)):
            label(caption,20,y-85,900,True)
            for index in range(first,last):
                x = 80+(index-first)*215
                positions.append((x,y))
                if index>first:
                    scene.addLine(x-215,y,x,y,QPen(accent,3))
        label_positions = [(x - 65, y + 24) for x, y in positions]
    for i, ((title,purpose,events,consequence), (x,y)) in enumerate(zip(steps,positions)):
        node = scene.addEllipse(x-9,y-9,18,18,QPen(accent,2),QBrush(QColor(palette.surface_raised)))
        node.setToolTip(f"{title}\n{purpose}\n\n{events}\n\n{consequence}")
        lx, ly = label_positions[i]
        text = label(f"{i+1:02d} · {title}",lx,ly)
        text.setToolTip(node.toolTip())
    scene.setSceneRect(scene.itemsBoundingRect().adjusted(-25,-25,25,25))
    return view
