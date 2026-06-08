# settings_screen.py  —  Look Away
# ─────────────────────────────────────────────────────────────────────────────
# run_settings(screen, clock)  → full settings UI, called from main menu
# run_controls(screen, clock)  → read-only controls reference page
# ─────────────────────────────────────────────────────────────────────────────

import pygame
import sys
from systems.settings_manager import settings

WHITE = (220, 220, 220)
RED   = (200,  40,  40)
DIM   = (120, 120, 120)
SECT  = ( 90, 110, 160)   # section header accent colour
DARK  = ( 10,  12,  20)


def _load_fonts():
    try:
        return {
            "title": pygame.font.Font("assets/fonts/menu_font.ttf", 46),
            "row":   pygame.font.Font("assets/fonts/menu_font.ttf", 24),
            "sect":  pygame.font.Font("assets/fonts/menu_font.ttf", 13),
            "hint":  pygame.font.Font("assets/fonts/menu_font.ttf", 15),
        }
    except Exception:
        return {
            "title": pygame.font.SysFont("courier", 46, bold=True),
            "row":   pygame.font.SysFont("courier", 24),
            "sect":  pygame.font.SysFont("courier", 13),
            "hint":  pygame.font.SysFont("courier", 15),
        }


def _bg(screen):
    """Draw the background — menu_bg with dark overlay, same as menu.py."""
    W, H = screen.get_size()
    try:
        bg = pygame.image.load("assets/images/menu_bg.png").convert()
        screen.blit(pygame.transform.scale(bg, (W, H)), (0, 0))
    except Exception:
        screen.fill(DARK)
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 155))
    screen.blit(ov, (0, 0))


def _recreate_display():
    """Rebuild the pygame display surface when fullscreen is toggled."""
    flags = pygame.SCALED
    if settings["fullscreen"]:
        flags |= pygame.FULLSCREEN
    pygame.display.set_mode((1280, 720), flags)


# ── CONTROLS PAGE ─────────────────────────────────────────────────────────────

def run_controls(screen, clock):
    fonts = _load_fonts()

    BINDINGS = [
        ("WASD  /  ARROWS",   "Move"),
        ("MOUSE",             "Aim flashlight"),
        ("LEFT CLICK",        "Throw wrench"),
        ("E",                 "Interact / Repair"),
        ("Q",                 "Use eye drop"),
        ("ESC",               "Pause"),
    ]

    while True:
        screen = pygame.display.get_surface()
        W, H   = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return   # any key goes back

        _bg(screen)

        # Panel
        PW, PH = 700, 380
        PX = W // 2 - PW // 2
        PY = H // 2 - PH // 2
        panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
        panel.fill((10, 12, 20, 235))
        screen.blit(panel, (PX, PY))
        pygame.draw.rect(screen, (50, 60, 80), (PX, PY, PW, PH), 2)

        # Title
        t = fonts["title"].render("CONTROLS", True, WHITE)
        screen.blit(t, (PX + PW // 2 - t.get_width() // 2, PY + 18))
        pygame.draw.line(screen, (50, 60, 80),
                         (PX + 20, PY + 68), (PX + PW - 20, PY + 68), 1)

        # Bindings
        for i, (key, action) in enumerate(BINDINGS):
            y = PY + 82 + i * 40
            screen.blit(fonts["row"].render(key,    True, RED),   (PX + 28, y))
            screen.blit(fonts["row"].render("—",    True, (55, 65, 85)), (PX + 258, y))
            screen.blit(fonts["row"].render(action, True, WHITE), (PX + 295, y))

        # Footer
        pygame.draw.line(screen, (50, 60, 80),
                         (PX + 20, PY + PH - 38),
                         (PX + PW - 20, PY + PH - 38), 1)
        h = fonts["hint"].render("press any key to go back", True, DIM)
        screen.blit(h, (PX + PW // 2 - h.get_width() // 2, PY + PH - 24))

        pygame.display.flip()
        clock.tick(60)


# ── SETTINGS PAGE ─────────────────────────────────────────────────────────────

# Each entry in _ITEMS is a dict describing one row.
# "header"  → section label, not selectable
# "toggle"  → left/right cycles through values[]
# "action"  → enter/right fires a callback
# "divider" → thin horizontal rule, not selectable

_ITEMS = [
    {"type": "header",  "label": "DISPLAY"},
    {"type": "toggle",  "label": "FULLSCREEN",      "key": "fullscreen",
     "values": [False, True],                 "display": ["OFF",    "ON"]},
    {"type": "toggle",  "label": "SHOW FPS",        "key": "show_fps",
     "values": [False, True],                 "display": ["OFF",    "ON"]},

    {"type": "header",  "label": "AUDIO"},
    {"type": "toggle",  "label": "MUSIC VOLUME",    "key": "music_volume",
     "values": [0.0, 0.25, 0.5, 0.75, 1.0],  "display": ["MUTE", "25%", "50%", "75%", "100%"]},
    {"type": "toggle",  "label": "SFX VOLUME",      "key": "sfx_volume",
     "values": [0.0, 0.25, 0.5, 0.75, 1.0],  "display": ["MUTE", "25%", "50%", "75%", "100%"]},

    {"type": "header",  "label": "GAMEPLAY"},
    {"type": "toggle",  "label": "SCREEN SHAKE",    "key": "screen_shake",
     "values": [False, True],                 "display": ["OFF",    "ON"]},
    {"type": "toggle",  "label": "DIALOGUE SPEED",  "key": "dialogue_speed",
     "values": ["NORMAL", "FAST"],            "display": ["NORMAL", "FAST"]},

    {"type": "divider"},
    {"type": "action",  "label": "VIEW CONTROLS"},
]

# Indices into _ITEMS that are actually selectable (not headers/dividers)
_SELECTABLE = [i for i, it in enumerate(_ITEMS)
               if it["type"] in ("toggle", "action")]


def _val_index(item):
    """Current index of this toggle's value in its values list."""
    cur = settings.get(item["key"])
    try:
        return item["values"].index(cur)
    except ValueError:
        return 0


def _apply(key):
    """Side-effects when a setting changes."""
    if key == "fullscreen":
        _recreate_display()
    elif key == "music_volume":
        pygame.mixer.music.set_volume(settings["music_volume"])
    # sfx_volume applied at play_sfx() call time
    # show_fps, screen_shake, dialogue_speed read per-frame — no action needed


def run_settings(screen, clock):
    fonts = _load_fonts()

    # sel_pos = index into _SELECTABLE list
    sel_pos   = 0
    n_sel     = len(_SELECTABLE)

    # Layout constants
    LBL_X     = 100      # left edge of label text
    VAL_CX    = 1000     # centre-x of value bracket
    ROW_H     = 47       # height per toggle/action row
    HDR_H     = 28       # height of a section header row
    DIV_H     = 22       # height of a divider row
    SECT_GAP  = 14       # extra gap ABOVE a section header (except the first)
    START_Y   = 130      # y of the first item

    while True:
        screen = pygame.display.get_surface()
        W, H   = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key in (pygame.K_UP, pygame.K_w):
                    sel_pos = (sel_pos - 1) % n_sel

                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel_pos = (sel_pos + 1) % n_sel

                # The actual item in _ITEMS that is currently focused
                focused = _ITEMS[_SELECTABLE[sel_pos]]

                if focused["type"] == "toggle":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        i = _val_index(focused)
                        settings[focused["key"]] = focused["values"][(i - 1) % len(focused["values"])]
                        _apply(focused["key"])

                    if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN):
                        i = _val_index(focused)
                        settings[focused["key"]] = focused["values"][(i + 1) % len(focused["values"])]
                        _apply(focused["key"])

                elif focused["type"] == "action":
                    if event.key in (pygame.K_RETURN, pygame.K_RIGHT, pygame.K_d):
                        run_controls(screen, clock)

        # ── DRAW ──────────────────────────────────────────────────────────
        _bg(screen)

        # Title + rule
        t = fonts["title"].render("SETTINGS", True, WHITE)
        screen.blit(t, (80, 55))
        pygame.draw.line(screen, (50, 60, 80), (80, 118), (W - 80, 118), 1)

        # Compute y positions for each item
        y = START_Y
        focused_item_idx = _SELECTABLE[sel_pos]

        for idx, item in enumerate(_ITEMS):
            itype = item["type"]

            if itype == "header":
                if idx > 0:          # gap above 2nd and 3rd section headers
                    y += SECT_GAP
                s = fonts["sect"].render(item["label"], True, SECT)
                screen.blit(s, (LBL_X - 2, y + 4))
                y += HDR_H

            elif itype == "divider":
                pygame.draw.line(screen, (45, 55, 75),
                                 (LBL_X, y + DIV_H // 2),
                                 (W - LBL_X, y + DIV_H // 2), 1)
                y += DIV_H

            elif itype == "toggle":
                is_sel = (idx == focused_item_idx)
                lbl_c  = RED if is_sel else WHITE

                if is_sel:
                    # Highlight band
                    band = pygame.Surface((W - 160, 38), pygame.SRCALPHA)
                    band.fill((200, 40, 40, 28))
                    screen.blit(band, (80, y - 2))
                    arr = fonts["row"].render(">", True, RED)
                    screen.blit(arr, (65, y))

                screen.blit(fonts["row"].render(item["label"], True, lbl_c), (LBL_X, y))

                # Value area:  < VALUE >
                vi      = _val_index(item)
                val_str = item["display"][vi]
                val_c   = RED if is_sel else DIM

                val_surf = fonts["row"].render(val_str, True, val_c)
                la = fonts["row"].render("<", True, val_c if is_sel else (55, 62, 78))
                ra = fonts["row"].render(">", True, val_c if is_sel else (55, 62, 78))
                total_w = la.get_width() + 10 + val_surf.get_width() + 10 + ra.get_width()
                vx = VAL_CX - total_w // 2
                screen.blit(la,       (vx, y))
                screen.blit(val_surf, (vx + la.get_width() + 10, y))
                screen.blit(ra,       (vx + la.get_width() + 10 + val_surf.get_width() + 10, y))
                y += ROW_H

            elif itype == "action":
                is_sel = (idx == focused_item_idx)
                lbl_c  = RED if is_sel else WHITE

                if is_sel:
                    band = pygame.Surface((W - 160, 38), pygame.SRCALPHA)
                    band.fill((200, 40, 40, 28))
                    screen.blit(band, (80, y - 2))
                    arr = fonts["row"].render(">", True, RED)
                    screen.blit(arr, (65, y))

                screen.blit(fonts["row"].render(item["label"], True, lbl_c), (LBL_X, y))
                open_s = fonts["row"].render("OPEN >", True, RED if is_sel else DIM)
                screen.blit(open_s, (VAL_CX - open_s.get_width() // 2, y))
                y += ROW_H

        # Footer
        pygame.draw.line(screen, (50, 60, 80),
                         (80, H - 52), (W - 80, H - 52), 1)
        hint = fonts["hint"].render(
            "W / S  navigate      A / D  change value      ESC  back",
            True, DIM)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 36))

        pygame.display.flip()
        clock.tick(60)
