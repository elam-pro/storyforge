"""Pure editing transitions and responsive paragraph geometry (no Qt)."""
ORDER = ('scene', 'action', 'character', 'dialogue', 'parenthetical', 'transition')
AFTER_RETURN = dict(zip(ORDER, ('action', 'character', 'dialogue', 'action', 'dialogue', 'scene')))


def cycle(current, reverse=False):
    index = ORDER.index(current) if current in ORDER else 1
    return ORDER[max(0, min(len(ORDER) - 1, index + (-1 if reverse else 1)))]


def after_return(current):
    return AFTER_RETURN.get(current, 'action')


def margins(element, viewport_width):
    width = max(520.0, float(viewport_width - 36))
    left, right, top, bottom = {
        'scene': (0, .02, 12, 6), 'action': (0, .05, 3, 6),
        'character': (.41, .17, 12, 1), 'dialogue': (.21, .21, 0, 5),
        'parenthetical': (.29, .29, 0, 1), 'transition': (.48, .02, 12, 8),
    }.get(element, (0, .05, 3, 6))
    return left * width, right * width, top, bottom
