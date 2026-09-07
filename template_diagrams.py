"""Native structural diagrams; positions illustrate a model, never grade a story."""
import math
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


def build_diagram(template, palette, parent=None):
    scene = QGraphicsScene(parent)
    view = QGraphicsView(scene)
    view.setObjectName("TemplateVisualCanvas")
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    steps, key = template["steps"], template["key"]
    circular = key in {"story_circle", "hero_journey"}
    accent = QColor(palette.accent)
    def label(text, x, y, width=190, muted=False):
        item = scene.addText(text)
        item.setTextWidth(width)
        item.setDefaultTextColor(QColor(palette.muted if muted else palette.text))
        item.setPos(x, y)
        return item
    label(template["title"], 20, 10, 900)
    label("Repères facultatifs · survole un point pour ses détails · glisse pour explorer", 20, 45, 900, True)
    if circular:
        cx, cy, radius = 420, 390, 225
        scene.addEllipse(cx-radius, cy-radius, radius*2, radius*2, QPen(accent, 3))
        label("DÉPART\n↓\nEXPÉRIENCE\n↓\nRETOUR TRANSFORMÉ", cx-90, cy-65, 180)
        positions = [(cx + radius*math.cos(-math.pi/2+i*math.tau/len(steps)),
                      cy + radius*math.sin(-math.pi/2+i*math.tau/len(steps))) for i in range(len(steps))]
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
    else:
        # Ordinal progression, explicitly not a universal tension or page-count curve.
        positions = [(80+i*220, 440-100*math.sin(i*math.pi/max(1,len(steps)-1))) for i in range(len(steps))]
        path = QPainterPath()
        path.moveTo(*positions[0])
        for x,y in positions[1:]:
            path.lineTo(x,y)
        scene.addPath(path, QPen(accent, 3))
        label("ORDRE DE LECTURE →  (espacement indicatif, sans durée imposée)", 20, 95, 850, True)
    for i, ((title,purpose,events,consequence), (x,y)) in enumerate(zip(steps,positions)):
        node = scene.addEllipse(x-9,y-9,18,18,QPen(accent,2),QBrush(QColor(palette.surface_raised)))
        node.setToolTip(f"{title}\n{purpose}\n\n{events}\n\n{consequence}")
        if circular:
            lx = x+18 if x>=420 else x-205
            ly = y-35
        elif key == "save_the_cat":
            lx, ly = x-65, y+24
        else:
            lx, ly = x-65, y+30 if i%2==0 else y-110
            scene.addLine(x,y+12 if i%2==0 else y-12,x,ly+12 if i%2==0 else ly+70,
                          QPen(QColor(palette.border_strong),1))
        text = label(f"{i+1:02d} · {title}",lx,ly)
        text.setToolTip(node.toolTip())
    scene.setSceneRect(scene.itemsBoundingRect().adjusted(-25,-25,25,25))
    return view
