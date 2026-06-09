import pygame
import sys
import cv2
import numpy


def run_level_select(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    cap = cv2.VideoCapture("assets/menu_video.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_delay = int(1000 / fps)
    last_frame_time = 0
    video_surface = None

    try:
        font_title = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 28)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font_title = pygame.font.SysFont("courier", 48, bold=True)
        font       = pygame.font.SysFont("courier", 28)
        font_small = pygame.font.SysFont("courier", 16)

    pages = [
        [
            {
                "name":         "LEVEL 1 — AWAKENING",
                "desc":         "Waking up in a crashed ship. No weapons.",
                "unlocked":     True,
                "level":        1,
                "gives_wrench": False,
            },
            {
                "name":         "LEVEL 2 — DESCENT",
                "desc":         "The moon grows closer. Find the wrench.",
                "unlocked":     True,
                "level":        2,
                "gives_wrench": False,
            },
            {
                "name":         "LEVEL 3 — THE VOICE",
                "desc":         "Something follows. Something speaks.",
                "unlocked":     True,
                "level":        3,
                "gives_wrench": True,
            },
        ],
        [
            {
                "name":         "LEVEL 4 — THE WATCHERS",
                "desc":         "The voice was wrong. Look away.",
                "unlocked":     True,
                "level":        4,
                "gives_wrench": True,
            },
            {
                "name":         "LEVEL 5 — THE THRESHOLD",
                "desc":         "All rules break here. Look away.",
                "unlocked":     True,
                "level":        5,
                "gives_wrench": True,
            },
            {
                "name":         "LEVEL 6 — THE CANNON",
                "desc":         "The truth. The choice. The end.",
                "unlocked":     True,
                "level":        6,
                "gives_wrench": True,
            },
        ],
    ]

    page     = 0
    selected = 0

    WHITE  = (220, 220, 220)
    DIM    = (100, 100, 100)
    RED    = (200,  40,  40)
    DARK   = ( 10,  12,  20)
    BORDER = ( 50,  60,  80)

    running = True
    while running:
        now = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()
        for i in range(len(pages[page])):
            cy = 180 + i * 120
            if pygame.Rect(80, cy, WIDTH - 160, 100).collidepoint(mx, my):
                selected = i

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cap.release()
                    return None

                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(pages[page])
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(pages[page])

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if page > 0:
                        page -= 1
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    if page < len(pages) - 1:
                        page += 1

                if event.key == pygame.K_RETURN:
                    lvl = pages[page][selected]
                    if lvl["unlocked"]:
                        cap.release()
                        return {
                            "level":        lvl["level"],
                            "gives_wrench": lvl["gives_wrench"],
                        }

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, lvl in enumerate(pages[page]):
                    cy = 180 + i * 120
                    if pygame.Rect(80, cy, WIDTH - 160, 100).collidepoint(mx, my):
                        if lvl["unlocked"]:
                            cap.release()
                            return {
                                "level": lvl["level"],
                                "gives_wrench": lvl["gives_wrench"],
                            }
                # Page navigation via mouse
                page_y = 180 + len(pages[page]) * 120 + 10
                if pygame.Rect(WIDTH // 2 - 100, page_y, 40, 30).collidepoint(mx, my):
                    page = max(0, page - 1)
                if pygame.Rect(WIDTH // 2 + 60, page_y, 40, 30).collidepoint(mx, my):
                    page = min(len(pages) - 1, page + 1)

        if now - last_frame_time >= frame_delay:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                video_surface = pygame.surfarray.make_surface(
                    numpy.rot90(numpy.fliplr(frame)))
            last_frame_time = now

        if video_surface:
            screen.blit(video_surface, (0, 0))
        else:
            screen.fill(DARK)

        # DARK OVERLAY
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # TITLE
        title = font_title.render("SELECT LEVEL", True, WHITE)
        screen.blit(title, (80, 60))

        hint = font_small.render(
            "W/S — navigate    A/D or ◄/► — switch page    ENTER — select    ESC — back",
            True, DIM)
        screen.blit(hint, (80, 120))

        # LEVEL CARDS
        card_x = 80
        card_y = 180
        card_w = WIDTH - 160
        card_h = 100
        gap    = 20

        for i, lvl in enumerate(pages[page]):
            cy = card_y + i * (card_h + gap)

            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if i == selected:
                card_surf.fill((30, 40, 60, 220))
            else:
                card_surf.fill((15, 18, 28, 200))
            screen.blit(card_surf, (card_x, cy))

            border_color = RED if i == selected else BORDER
            pygame.draw.rect(screen, border_color,
                             (card_x, cy, card_w, card_h), 2)

            if lvl["unlocked"]:
                if i == selected:
                    arrow = font.render(">", True, RED)
                    screen.blit(arrow, (card_x + 15, cy + card_h // 2 - 14))

                name_color = RED if i == selected else WHITE
                name = font.render(lvl["name"], True, name_color)
                screen.blit(name, (card_x + 45, cy + 18))

                desc = font_small.render(lvl["desc"], True, DIM)
                screen.blit(desc, (card_x + 45, cy + 58))

                if lvl["gives_wrench"]:
                    wrench = font_small.render(
                        "[ WRENCH PROVIDED ]", True, (180, 140, 80))
                    screen.blit(wrench, (card_x + card_w - 220, cy + 38))
            else:
                locked = font.render(
                    lvl["name"] + "  [ LOCKED ]", True, (60, 60, 60))
                screen.blit(locked, (card_x + 45, cy + 35))

        # PAGE INDICATOR
        page_str  = f"< {page + 1} / {len(pages)} >"
        page_text = font_small.render(page_str, True, (160, 160, 200))
        screen.blit(page_text,
                    (WIDTH // 2 - page_text.get_width() // 2,
                     card_y + len(pages[page]) * (card_h + gap) + 10))

        pygame.display.flip()
        clock.tick(60)